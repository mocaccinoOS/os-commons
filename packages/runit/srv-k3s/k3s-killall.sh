#!/bin/sh

runit-stop k3s
pstree() {
    for pid in $@; do
        echo $pid
        pstree $(ps -o ppid= -o pid= | awk "\$1==$pid {print \$2}")
    done
}
killtree() {
    [ $# -ne 0 ] && kill $(set +x; pstree $@; set -x)
}

for p in $(lsof | sed -e 's/^[^0-9]*//g; s/  */\t/g' | grep -w 'k3s/data/[^/]*/bin/containerd-shim' | cut -f1 | sort -n -u); do
killtree $p 
done
do_unmount() {
    MOUNTS=`cat /proc/self/mounts | awk '{print $2}' | grep "^$1" | sort -r`
    if [ -n "${MOUNTS}" ]; then
        umount ${MOUNTS}
    fi
}
do_unmount '/run/k3s'
do_unmount '/var/lib/docker'
do_unmount '/var/lib/kubelet'
do_unmount '/var/run/netns'
do_unmount '/var/lib/rancher/k3s'

nets=$(ip link show | grep 'master cni0' | awk -F': ' '{print $2}' | sed -e 's|@.*||')
for iface in $nets; do
    ip link delete $iface;
done
ip link delete cni0
ip link delete flannel.1
rm -rf /var/lib/cni/
