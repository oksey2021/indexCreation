#! /bin/bash

export HOST_FILE="54.242.194.181"

export SSH_USER="ec2-user"

export REMOTE_INSTALL_SCRIPT="/home/ec2-user/indexes.conf /home/ec2-user/indexes

sudo cp /home/ec2-user/indexes.conf /home/splunk/

sudo chown -R splunk:splunk /home/splunk

sudo -u splunk diff /home/splunk/indexes /opt/splunk/etc/system/default/indexes.conf | grep '>' | cut -c 3- >>  /opt/splunk/etc/system/local/indexes.conf"


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
scp /var/lib/jenkins/workspace/firstJob/master-apps/all_indexes_user/local/indexes.conf ec2-user@54.242.194.181:.
echo "---------------------------"
echo "Reading to the host"
ssh -i /var/lib/jenkins/.ssh/oksey2022.pem ec2-user@54.242.194.181 "$REMOTE_INSTALL_SCRIPT"
#ssh -t "$i" "$REMOTE_INSTALL_SCRIPT"
echo "---------------------------"
echo "Done"          
