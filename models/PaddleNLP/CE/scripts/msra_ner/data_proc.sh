
#获取当前路径
cur_path=`pwd`
model_name=${PWD##*/}
echo "$model_name 模型数据预处理阶段"
#配置目标数据存储路径
root_path=$cur_path/../../
code_path=$cur_path/../../models_repo/examples/information_extraction/msra_ner/
# 打印出paddlenlp datasets路径
python print_path.py
#临时环境更改
cd $root_path/models_repo && ls
cd $code_path
#获取数据&模型逻辑
#数据处理逻辑
# 跑之前先修改下包的代码：
echo "删除之前先打印出来"
cat /usr/local/lib/python3.8/dist-packages/datasets/builder.py
sed -i '557,561d' /usr/local/lib/python3.8/dist-packages/datasets/builder.py
echo "删除之后再打印出来"
cat /usr/local/lib/python3.8/dist-packages/datasets/builder.py
