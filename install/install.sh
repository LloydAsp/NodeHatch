#!/bin/bash

## install lxd
apt-get update
apt-get install -y snapd
snap install lxd

PATH="$PATH:/snap/bin"

## import certificate
cat > lxc.crt <<- EOF
-----BEGIN CERTIFICATE-----
MIIDETCCAfkCFD85IzHu/+Tl6lXSm2svOuV1b/lfMA0GCSqGSIb3DQEBCwUAMEUx
CzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRl
cm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMjMwNzI1MDgzMjUxWhcNMzMwNzIyMDgz
MjUxWjBFMQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UE
CgwYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOC
AQ8AMIIBCgKCAQEAy0BAUWKCpayUlZZFDhLJdL2nJ78JH51eFlVwErY2qDKsl6GZ
pIQuaTjKxNfcsF2RkmkZ9hb5OPYDu7kD9vXFkJtWir+aVZkXxXirOCy0JNifpNZq
A7APSVQQL/zOErG98y74o5Y5CzW4V3hT0VaXb+FwV5sJB3SjYR9Xsh9VOkGvngxU
GZHrsgtmMqRW9NDVZu7+PBnAyvcNB9VzK+1rPbMbPSWBQdGiQZ4eiPhtQbgWsiGq
gNRwZbD4JAa9biDT3GW2DrCtc2KEsXdBmvnoNBJ/lg+lQPqP4LMEFvLm7PHAQMI8
ei4lAiYsE1Pquv3peehIz3EvMljMR5+5amD4jwIDAQABMA0GCSqGSIb3DQEBCwUA
A4IBAQCbYRVZn/0tfumXGAe3uJ9LcyPWA6wSB5oi1b58/M5SSsOrThxnN6GNMKJg
Ql472LOL2DlIi0h1cd76AAHzu2hTVWaQ0SyOyPP5afXicJnHDEJdNow3Bbdht+zj
4Iq9g9gbERuSUfICzquSP2SqLkUx9HaCdFk2FDkDJqWCpAbTKyT1vYiflwvguQEE
4dOyNxUiY4uwEtbMlCV5k4LlHB1srtWm3I/a8eCCUnnycsn/7TBKqeTt7kfbUTr7
seHHTrV3+EYkmTHzdvnB8Mo2NcSlvCF7SJxpRs/Uv8/lVt1ez8HOECCxk62jTq7g
VSTrk5DR28HDDbJEbjTghMv6xPhA
-----END CERTIFICATE-----
EOF
lxc config trust add lxc.crt
rm lxc.crt


## init
/snap/bin/lxd init --auto --network-address=[::] --network-port=8443 --storage-backend=btrfs --storage-create-loop=5
sleep 1

## create project
lxc project create NodeHatch -c features.images=true -c features.profiles=false
sleep 1
lxc project switch NodeHatch

## import template
wget -O alpine3.18-minimal.tar.gz https://github.com/LloydAsp/templates/releases/download/v1.0.0/alpine3.18-minimal.tar.gz
wget -O debian11.tar.gz https://github.com/LloydAsp/templates/releases/download/v1.0.0/debian11.tar.gz
wget -O debian-11-vm-cloud-ssh.tar.gz https://github.com/LloydAsp/templates/releases/download/v1.0.0/debian-11-vm-cloud-ssh.tar.gz
lxc image import alpine3.18-minimal.tar.gz --alias alpine-3.18-ssh
lxc image import debian11.tar.gz --alias debian-11-ssh
lxc image import debian-11-vm-cloud-ssh.tar.gz --alias debian-11-vm-cloud-ssh
rm alpine3.18-minimal.tar.gz debian11.tar.gz debian-11-vm-cloud-ssh.tar.gz

lxc project switch default

echo 'install finished, application is listening at port 8443, please add your public ip and port in the panel'
echo '安装完成，程序监听端口为8443，请在面板添加你的公网ip和端口'
