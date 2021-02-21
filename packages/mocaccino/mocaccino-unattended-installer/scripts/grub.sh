#!/bin/bash

cat <<'EOF'
   .       . 
 +  :      .
           :       _
       .   !   '  (_)
          ,|.' 
-  -- ---(-O-`--- --  -
         ,`|'`.
       ,   !    .
           :       :  " 
           .     --+--
 .:        .       !
EOF

echo "Generating initramfs and grub setup"

BOOTDIR=$TARGET/boot

CURRENT_KERNEL=$(ls $BOOTDIR/kernel-*)
export KERNEL_GRUB=${CURRENT_KERNEL/${BOOTDIR}/}
export INITRAMFS=${CURRENT_KERNEL/kernel/initramfs}
export INITRAMFS_GRUB=${INITRAMFS/${BOOTDIR}/}

if [[ ! -e "$TARGET/boot/Initrd" ]] || [[ -L "$TARGET/boot/Initrd" ]]; then
  luet geninitramfs "${INITRAMFS_PACKAGES}"
  pushd $TARGET/boot/
  rm -rf Initrd
  ln -s initramfs* Initrd
  popd
fi

mkdir -p ${TARGET}/boot/grub
cat > ${TARGET}/boot/grub/grub.cfg << EOF
set default=0
set timeout=10
set gfxmode=auto
set gfxpayload=keep
insmod all_video
insmod gfxterm
menuentry "MocaccinoOS" {
  linux /bzImage root=${INSTALL_DEVICE}4
  initrd /Initrd
}
EOF

# grub-mkconfig -o /boot/grub/grub.cfg
GRUB_TARGET=
if [ -e "/sys/firmware/efi" ]; then
  GRUB_TARGET="--target=x86_64-efi --efi-dir=/boot/efi"
  mkdir -p ${TARGET}/boot/efi
fi

chroot ${TARGET} /bin/sh <<EOF
echo "GRUB_CMDLINE_LINUX_DEFAULT=\"root=${INSTALL_DEVICE}4\"" >> /etc/default/grub
grub-install ${GRUB_TARGET} ${INSTALL_DEVICE}
EOF

