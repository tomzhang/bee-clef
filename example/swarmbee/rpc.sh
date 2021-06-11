#!/bin/bash
add-apt-repository -y ppa:git-core/ppa
apt-get -y update
apt-get install -y git
apt-get install -y software-properties-common
add-apt-repository -y ppa:ethereum/ethereum
apt-get -y update
apt-get install -y ethereum
apt-get install -y screen
if [ ! -f /etc/systemd/system/rpc.service ]; then
cat >> /etc/systemd/system/rpc.service << EOF
[Unit]
Description=Geth GoErli
[Service]
User=root
LimitNOFILE=65536
ExecStart=/usr/bin/geth --cache=1024 --goerli  --datadir /data --http --http.addr 0.0.0.0 --http.port=8545 --http.vhosts="*" --http.api='personal,eth,net,web3,admin,txpool' --ws --ws.addr=0.0.0.0 --ws.port=8546 --ws.api='personal,eth,net,web3,admin' --ws.origins="*"
KillSignal=SIGINT Restart=on-failure
RestartSec=30
StartLimitInterval=350
StartLimitBurst=10
[Install]
WantedBy=multi-user.target
EOF
echo '服务已安装成功'
else echo '服务已经存在'
fi
# 重新加载配置
systemctl daemon-reload
# 使bee服务生效
systemctl enable rpc
# 启动bee
systemctl start rpc
#显示状态
echo '============================================================='
echo '显示运行状态输入：systemctl status rpc'
echo '运行log存放在：/var/log/rpc.log'
echo '欢迎使用中文手册：https://docs.swarmetm.org'
echo '==================================Aven7======================='
systemctl status rpc
