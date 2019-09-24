#!/bin/bash

CMD="$*"

bp()
{
    pkg="$1";shift
    ver="$1";shift
    flag="$1";shift
    bz="$1";shift
    origbranch="$1";shift
    brew="$1";shift
    brewid="$1";shift
    workbranch="omega4amd/$pkg-$ver"
    patchfile="/tmp/omega4/$pkg-$ver.patch"
    bzurl="https://bugzilla.redhat.com/show_bug.cgi?id=$bz"

    eval "$CMD"
    return

    if [ -z "$brew" ];then
        git reset --hard && \
        git checkout $workbranch && \
        sed -i -e '/%%CHANGELOG%%/d' redhat/qemu-kvm.spec.template && \
        make -C redhat rh-brew | tee /tmp/$pkg-$ver.brew
    fi

    git format-patch $workbranch^..$workbranch --stdout > $patchfile
    sed -i -e '/^New microcode/i \
Bugzilla: \
Brew: \
' $patchfile
    sed -i -e "s@^Bugzilla: @Bugzilla: $bzurl@" $patchfile
    sed -i -e "s@Subject: \\[PATCH\\]@Subject: [$pkg $ver PATCH]@" $patchfile
    sed -i -e "s@^Brew: @Brew: $brew@" $patchfile
}

#  ver        flag         BZ
bp qemu-kvm 6.9.z      rhel-6.9.z   1574067   rhel6/rhel69/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16151499' 16151499
#bp qemu-kvm 6.8.z      rhel-6.8.z   ''        rhel6/rhel68/master
bp qemu-kvm 6.7.z      rhel-6.7.z   1574072   rhel6/rhel67/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16151510' 16151510
bp qemu-kvm 6.6.z      rhel-6.6.z   1574071   rhel6/rhel66/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16151515' 16151515
bp qemu-kvm 6.5.z      rhel-6.5.z   1574068   rhel6/rhel65/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16151518' 16151518
bp qemu-kvm 6.4.z      rhel-6.4.z   1574066   rhel6/rhel64/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16151471' 16151471
bp qemu-kvm 6.10       rhel-6.10    1574074   rhel6/rhel6/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16150672' 16150672

bp qemu-kvm-rhev 7.5.z      rhel-7.5.z   1574075   rhel7/rhv7/master-2.10.0 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16153165' 16153165
bp qemu-kvm-rhev 7.4.z      rhel-7.4.z   1574070   rhel7/rhv7/master-2.9.0 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16153348' 16153348
bp qemu-kvm-rhev 7.3.z      rhel-7.3.z   1574073   rhel7/rhev7/master-2.6.0 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16153603' 16153603
bp qemu-kvm-rhev 7.2.z      rhel-7.2.z   1574069   rhel7/rhev7/master-2.3.0 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16153746' 16153746
bp qemu-kvm-rhev 7.6        rhel-7.6     1574082   rhel7/rhv7/master-2.12.0 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16151161' 16151161

bp qemu-kvm 7.5.z      rhel-7.5.z   1574075   rhel7/rhel75/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16152845' 16152845
bp qemu-kvm 7.4.z      rhel-7.4.z   1574070   rhel7/rhel74/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16153044' 16153044
bp qemu-kvm 7.3.z      rhel-7.3.z   1574073   rhel7/rhel73/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16153833' 16153833
bp qemu-kvm 7.2.z      rhel-7.2.z   1574069   rhel7/rhel72/master 'https://brewweb.engineering.redhat.com/brew/taskinfo?taskID=16152723' 16152723
bp qemu-kvm 7.6        rhel-7.6     1574082   rhel7/rhel7/master
