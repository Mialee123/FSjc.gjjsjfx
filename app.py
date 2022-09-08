import pandas as pd
import streamlit as st
from streamlit.elements.image import image_to_url
from PIL import Image
import datetime

   
#下载模板文件
def template_download():
    with open("template.xlsx", "rb") as file:
        btn=st.sidebar.download_button(label="请下载模板文件",data=file,file_name="template.xlsx")

#上传分析文件    
def excel_upload():
    global uploaded_file#全局变量
    uploaded_file=st.sidebar.file_uploader("上传分析文件",type="xlsx")

#输入限制参数
def boundary_num():
    global max_m
    global min_m
    max_m=st.sidebar.slider("设定提取后个人账户余额的最大值", min_value=10000, max_value=1000000, value=50000, step=1000)
    min_m=st.sidebar.slider("设定提取公积金金额最小值", min_value=10000, max_value=100000, value=5000, step=100)
    st.write('当前设定提取后个人账户余额的最大值为', max_m)
    st.write('当前设定提取公积金金额最小值为', min_m)
    
#读取上传文件    
def upload_read():        
    global mf
    mf=pd.read_excel(uploaded_file,usecols='A:H')
    
def amount_analyse():
    mf.drop(mf[(mf.提取后个人账户余额>max_m)|(mf.提取金额<min_m)].index,inplace=True)
    mf.to_excel(uploaded_file,sheet_name='Sheet2',index=False)
    global df
    df=pd.read_excel(uploaded_file,sheet_name='Sheet2',usecols='A:H')
    global df_unit
    result=df['所属管理部'].value_counts()
    result.to_excel(uploaded_file,sheet_name='Sheet3')
    df_unit=pd.read_excel(uploaded_file,sheet_name='Sheet3')
    df_unit.columns=["unit","times"]
    df_unit.dropna(inplace=True)


def slider_amount():
    # streamlit的多重选择(选项数据)
    department = df['所属管理部'].unique().tolist()
    # streamlit的滑动条(金额范围)
    amounts= df['提取金额'].unique().tolist()
    # 滑动条, 最大值、最小值、区间值
    amount_selection=st.slider('提取金额:',
                          min_value=min(amounts),
                          max_value=max(amounts),
                          value=(min(amounts), max(amounts)))

    # 多重选择, 默认全选
    department_selection = st.multiselect('所属管理部:',
                                      department,
                                      default=department)
    # 根据选择过滤数据
    mask = (df['提取金额'].between(*amount_selection)) & (df['所属管理部'].isin(department_selection))
    number_of_result = df[mask].shape[0]

    # 根据筛选条件, 得到有效数据
    st.markdown(f'*有效数据: {number_of_result}*')

    # 根据选择分组数据
    df_grouped = df[mask].groupby(by=['收款户名']).count()[['提取金额']]
    df_grouped = df_grouped.rename(columns={'提取金额': '计数'})
    df_grouped = df_grouped.reset_index()
    # 绘制柱状图, 配置相关参数
    bar_chart = px.bar(df_grouped,
                   x='收款户名',
                   y='计数',
                   text='计数',
                   color_discrete_sequence=['#66CCCC']*len(df_grouped),
                   template='plotly_white')
    st.plotly_chart(bar_chart)
    st.dataframe(df[mask], width=1500)


def pv_pieShowtimes():
    #在饼图中，显示不同公积金部门执行次数
    pv_piechart=px.pie(df_unit,title="区域分布",values="times",names="unit")
    st.plotly_chart(pv_piechart)


#图片展示
def imageShow():
    image=Image.open("上传文件提示.jpg")#在未导入excel时，展示图片
    st.sidebar.image(image, clamp=False,
             channels="RGB",output_format="auto")

st.set_page_config(
     page_title="分析结果",
     page_icon="🏫",
     layout="wide",
     initial_sidebar_state="expanded"
 )
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.header('住房公积金扣划金额数据可视化分析1.0')
st.image('bg.jpg', clamp=False,width=None,channels="RGB",output_format="auto",caption='Design By FSJC.LiNing',use_column_width=None)
st.sidebar.title('数据上传')
template_download()
boundary_num()
excel_upload()
if uploaded_file is not None: 
      upload_read()
      st.sidebar.success("上传成功")
      amount_analyse()
      slider_amount()
      pv_pieShowtimes()
    #否则展示图片   
else:imageShow()







