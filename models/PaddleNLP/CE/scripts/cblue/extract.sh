#外部传入参数说明
# $1: 'single' 单卡训练； 'multi' 多卡训练； 'recv' 恢复训练
# $2:  $XPU = gpu or cpu
#获取当前路径
cur_path=`pwd`
model_name=${PWD##*/}

echo "$model_name 模型训练阶段"
#取消代理
HTTPPROXY=$http_proxy
HTTPSPROXY=$https_proxy
unset http_proxy
unset https_proxy

#路径配置
root_path=$cur_path/../../
code_path=$cur_path/../../models_repo/examples/benchmark/cblue/
log_path=$root_path/log/$model_name/
if [ ! -d $log_path ]; then
  mkdir -p $log_path
fi


#访问RD程序
cd $code_path
unset CUDA_VISIBLE_DEVICES

print_info(){
cat ${log_path}/$2.log
if [ $1 -ne 0 ];then
    echo "exit_code: 1.0" >> ${log_path}/$2.log
else
    echo "exit_code: 0.0" >> ${log_path}/$2.log
fi
}

if [[ $1 == 'gpu' ]];then #GPU
    python -m paddle.distributed.launch --gpus $3 train_spo.py \
        --batch_size 12 \
        --max_seq_length 300 \
        --learning_rate 6e-5 \
        --epochs 1 \
        --use_amp True \
        --max_steps 10 \
        --save_steps 10 \
        --logging_steps 1 \
        --valid_steps 100 \
        --save_dir ./checkpoint/CMeIE/$2 > $log_path/extract_$2_$1.log 2>&1
    print_info $? extract_$2_$1
fi

export http_proxy=$HTTPPROXY
export https_proxy=$HTTPSPROXY
