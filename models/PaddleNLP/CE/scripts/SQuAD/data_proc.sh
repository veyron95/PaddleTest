
#获取当前路径
cur_path=`pwd`
model_name=${PWD##*/}
echo "$model_name 模型数据预处理阶段"
#配置目标数据存储路径
root_path=$cur_path/../../
code_path=$cur_path/../../models_repo/examples/machine_reading_comprehension/SQuAD/
#临时环境更改
cd $root_path/models_repo && ls
cd $code_path
#获取数据&模型逻辑
# 删除之前先打印出来
echo "删除之前先打印出来"
cat /opt/_internal/cpython-3.7.0/lib/python3.7/site-packages/datasets/builder.py
sed -i '557,561d' /opt/_internal/cpython-3.7.0/lib/python3.7/site-packages/datasets/builder.py
echo "删除之后再打印出来"
cat /opt/_internal/cpython-3.7.0/lib/python3.7/site-packages/datasets/builder.py
