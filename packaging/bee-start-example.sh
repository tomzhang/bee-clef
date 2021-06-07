###
 # @Author: 张明锋
 # @Date: 2021-05-20 13:55:05
 # @LastEditTime: 2021-05-20 13:55:28
 # @LastEditors: Please set LastEditors
 # @Description: In User Settings Edit
 # @FilePath: /bee-clef/packaging/bee-start-example.sh
###


docker run \
  --name Tbee7 \
  -v /home/bee/bee/bee7:/root/.bee \
  --user "$(id -u):$(id -g)" \
  -p 1633:1633 \
  -p 1634:1634 \
  -p 1635:1635 \
  --restart=always   -it  ethersphere/bee:0.5.3 \
  start \
    --verbosity 5 \
    --password-file /root/.bee/password \
    --swap-endpoint https://goerli.infura.io/v3/6c2ba943b3d14a7695af1ede3f5247e5  \
    --debug-api-enable