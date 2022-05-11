#! /bin/bash

export HOST_FILE="/Users/oluwaseunoke/hostlist"

export PRIVATE_KEY_PATH="/Users/oluwaseunoke/tekstream.pem"

export SSH_USER="ec2-user"

export REMOTE_INSTALL_SCRIPT="sudo yum install wget -y

sudo wget -O splunk-8.2.4-87e2dda940d1-Linux-x86_64.tgz 'https://download.splunk.com/products/splunk/releases/8.2.4/linux/splunk-8.2.4-87e2dda940d1-Linux-x86_64.tgz'

sudo tar -xvzf splunk-8.2.4-87e2dda940d1-Linux-x86_64.tgz -C /opt

sudo rm -rf splunk-8.2.4-87e2dda940d1-Linux-x86_64.tgz

sudo useradd splunk

sudo usermod --password welcome90 splunk

sudo usermod -a -G wheel splunk

sudo chown -R splunk:splunk /opt/splunk

sudo -u splunk /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt --seed-passwd welcome90

sudo /opt/splunk/bin/splunk enable boot-start -user splunk

sudo -u splunk  /opt/splunk/bin/splunk status

sudo -u splunk  /opt/splunk/bin/splunk version

sudo -u splunk /opt/splunk/bin/splunk enable web-ssl -auth admin:welcome90

sudo -u splunk /opt/splunk/bin/splunk restart"


### ========================================== ###
###              SCRIPT EXECUTION              ###
### ========================================== ###

#The remote script above is executed below and will go through your hostlist file and host by host create a backup and upgrade each splunk instance.

echo "In 5 seconds, will run the following script on each remote host:"
echo
echo "===================="
echo "$REMOTE_INSTALL_SCRIPT"
echo "===================="
echo
sleep 5
echo "Reading host logins from $HOST_FILE"
echo
echo "Starting."
for i in `cat "$HOST_FILE"`; do
if [ -z "$i" ]; then
continue;
fi
echo "---------------------------"
echo "Installing to $i"
ssh -i $PRIVATE_KEY_PATH -t "$SSH_USER@$i" "$REMOTE_INSTALL_SCRIPT"
#ssh -t "$i" "$REMOTE_INSTALL_SCRIPT"
done
echo "---------------------------"
echo "Done"
~             
