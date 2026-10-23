import os, csv, io, json
import streamlit as st
from engine import load_books,save_books,recommend,fallback_script,use_llm

st.set_page_config(page_title='书播助手 · BookLive',page_icon='📚',layout='wide')
st.markdown('''<style>
.block-container {padding-top:2rem;max-width:1250px;}
[data-testid="stMetric"] {background:#f6f8fa;border:1px solid #e6eaf0;border-radius:14px;padding:12px;}
h1 {letter-spacing:-1px;}
</style>''',unsafe_allow_html=True)

# Streamlit Cloud secrets may not be exported as environment variables automatically.
try:
    for name in ('OPENAI_API_KEY', 'OPENAI_MODEL', 'BOOKLIVE_ALLOW_EDIT'):
        if name in st.secrets and name not in os.environ:
            os.environ[name] = str(st.secrets[name])
except (FileNotFoundError, KeyError):
    pass

# Public shared demos are read-only by default. Set BOOKLIVE_ALLOW_EDIT=1 only for trusted private deployments.
allow_edit = os.getenv('BOOKLIVE_ALLOW_EDIT', '0') == '1'
books=load_books()
st.title('📚 BookLive · AI 图书直播助手')
st.caption('V0.2 公开体验原型｜演示图书信息非真实库存｜人工审核后使用，不接入直播平台')

with st.sidebar:
    st.header('运行设置')
    has_key=bool(os.getenv('OPENAI_API_KEY'))
    mode=st.toggle('启用大模型生成',value=False,disabled=not has_key)
    if has_key:
        model=st.text_input('模型名称',value=os.getenv('OPENAI_MODEL','gpt-4.1-mini'))
        st.caption('调用 API 可能产生费用。密钥仅从环境变量读取。')
    else:
        model=''
        st.info('当前为免费离线演示模式。设置 OPENAI_API_KEY 后可启用真实大模型。')
    st.divider()
    st.markdown('**产品边界**')
    st.caption('不自动采集平台评论、不自动发言、不朗读整本书；演示内容须核实。')

available=sum(int(b.get('stock',0) or 0)>0 for b in books)
c1,c2,c3=st.columns(3)
c1.metric('图书条目',len(books));c2.metric('有库存图书',available);c3.metric('运行模式','AI 模式' if mode else '离线演示')

t1,t2,t3,t4=st.tabs(['📖 书目管理','🎙️ 直播介绍词','💬 评论问答与推荐','🧪 试播记录'])
with t1:
    st.subheader('图书知识库')
    st.caption('示例数据仅用于演示，不代表真实书店库存或价格。请使用获得授权的商品信息。')
    if books:
        st.dataframe([{k:b.get(k,'') for k in ('title','author','category','stock','description','audience','keywords')} for b in books],use_container_width=True,hide_index=True)
    else: st.warning('书目为空，请添加图书。')
    if not allow_edit:
        st.info('公开体验版已锁定书库修改功能，避免不同访客之间互相覆盖数据。')
    if allow_edit:
      with st.expander('新增一本书',expanded=False):
          with st.form('add_book'):
              title=st.text_input('书名 *');author=st.text_input('作者');category=st.text_input('分类');stock=st.number_input('库存',min_value=0,value=10,step=1)
              description=st.text_area('真实商品简介（建议来自出版社授权信息）');audience=st.text_input('适合人群');keywords=st.text_input('标签，用逗号分隔')
              if st.form_submit_button('加入书库',type='primary'):
                  if not title.strip():st.error('请填写书名')
                  elif any(b.get('title')==title.strip() for b in books):st.error('书名已存在，请修改原数据或使用不同标题。')
                  else:
                      books.append(dict(title=title.strip(),author=author,category=category,stock=int(stock),description=description,audience=audience,keywords=keywords));save_books(books);st.success('已保存');st.rerun()
    st.markdown('#### 批量导入 / 导出')
    export=io.StringIO();fields=['title','author','category','stock','description','audience','keywords']
    writer=csv.DictWriter(export,fieldnames=fields);writer.writeheader();writer.writerows([{k:b.get(k,'') for k in fields} for b in books])
    st.download_button('下载当前书库 CSV',export.getvalue().encode('utf-8-sig'),file_name='books.csv',mime='text/csv')
    upload=st.file_uploader('上传 CSV（UTF-8 或 UTF-8 BOM）',type=['csv']) if allow_edit else None
    if allow_edit and upload is not None and st.button('导入 CSV（同名条目覆盖）'):
        try:
            content=upload.getvalue().decode('utf-8-sig')
            incoming=list(csv.DictReader(io.StringIO(content)))
            if 'title' not in (incoming[0].keys() if incoming else []): raise ValueError('缺少 title 列')
            merged={b['title']:b for b in books}
            for row in incoming:
                if not row.get('title','').strip():continue
                try: row['stock']=max(0,int(row.get('stock') or 0))
                except ValueError:row['stock']=0
                merged[row['title'].strip()]={k:row.get(k,'') for k in fields}
            save_books(list(merged.values()));st.success(f'导入完成：{len(incoming)} 行');st.rerun()
        except Exception as ex:st.error(f'导入失败：{ex}')
with t2:
    st.subheader('直播口播稿')
    if not books:st.info('先添加书目。')
    else:
        picked=st.selectbox('当前讲解书籍',[b['title'] for b in books]);duration=st.radio('预计口播时长',['30秒','60秒'],horizontal=True)
        book=next(b for b in books if b['title']==picked)
        st.caption(f"商品资料：{book.get('description','未填写')}  |  库存：{book.get('stock',0)}")
        if st.button('生成口播稿',type='primary'):
            if mode:
                try: answer=use_llm(f'只给《{picked}》写一段适合约{duration}直播口播的自然介绍，不承诺无法核实的事实；结尾加一个互动问题。', [book],model)
                except Exception as ex:st.error(f'大模型调用失败：{ex}');answer=''
            else:answer=fallback_script(book,duration)
            if answer:st.session_state['script']=answer
        if 'script' in st.session_state:
            st.text_area('可复制、可人工修改的文案',key='script',height=210)
            st.caption('V0.1 未实现语音合成；下一版本可接入 TTS。')
with t3:
    st.subheader('主播评论问答台')
    question=st.text_area('输入一条观众评论',placeholder='例如：想了解商业和科技，有没有适合大学生的入门书？',height=90)
    if st.button('分析评论并推荐',type='primary'):
        if not question.strip():st.warning('请输入评论。')
        else:
            picks=recommend(question,books)
            st.session_state['recommendations']=picks
            st.session_state['last_question']=question
            if mode:
                try:
                    st.session_state['reply']=use_llm('请针对观众评论给主播生成建议回复；只能推荐下列图书，并解释推荐原因，不存在适合书目时明确说明。观众评论：'+question,picks,model)
                except Exception as ex:st.error(f'模型调用失败：{ex}');st.session_state['reply']=''
            else:
                if picks:st.session_state['reply']='可以先看看'+ '、'.join('《'+b['title']+'》' for b in picks) +'。这几本与您提到的关键词有一定关联，建议结合具体内容和试读再判断。（规则匹配演示，需人工审核）'
                else:st.session_state['reply']='目前在有库存的书目中没有找到明显匹配项，建议主播询问读者更具体的偏好。'
    if 'reply' in st.session_state:
        st.markdown('**建议回复（请人工确认后使用）**')
        st.info(st.session_state['reply'])
        st.markdown('**推荐书目**')
        picks=st.session_state.get('recommendations',[])
        if picks:
            for i,b in enumerate(picks,1):
                st.markdown(f"**{i}.《{b['title']}》** · {b.get('category','')} · 库存 {b.get('stock',0)}")
                st.caption(b.get('description','暂无说明'))
        else:st.caption('无匹配结果')
        st.warning('离线模式仅是简单关键词匹配，不是真正的语义推荐。') if not mode else None
with t4:
    st.subheader('试播验证记录')
    st.markdown('''建议首次试播记录四项：**主播准备时间、有效问题数、AI 建议可用数、主播实际采用数**。\n\n真实直播数据请先取得书店许可，再导入或人工记录。当前版本不连接任何直播平台。''')
    with st.form('pilot'):
        prep_before=st.number_input('原准备时长（分钟）',min_value=0,value=60)
        prep_after=st.number_input('使用助手后准备时长（分钟）',min_value=0,value=40)
        questions=st.number_input('本场有效问题数',min_value=0,value=20)
        usable=st.number_input('AI 建议经人工审核可用数',min_value=0,value=12)
        adopted=st.number_input('主播实际采用数',min_value=0,value=8)
        if st.form_submit_button('计算试播结果'):
            if usable>questions or adopted>usable:st.error('数据关系应满足：实际采用 ≤ 可用建议 ≤ 有效问题。')
            else:
                st.metric('节约准备时间',f'{max(0,prep_before-prep_after)} 分钟')
                st.metric('建议可用率',f'{usable/questions:.1%}' if questions else '无数据')
                st.metric('建议采用率',f'{adopted/questions:.1%}' if questions else '无数据')
