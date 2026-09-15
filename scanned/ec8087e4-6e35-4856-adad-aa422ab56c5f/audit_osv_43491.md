# [H] cifs: remove all cifs files before kill super

## Summary
Severity: High
Advisory: CVE-2026-74259
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74259
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: remove all cifs files before kill super

Cifs files may be put into fileinfo_put_wq during umounting cifs.
After umount done, cifsFileInfo_put_final is called, which cause
following BUG:

BUG: kernel NULL pointer dereference, address: 0000000000000000
...
[  134.222152]  list_lru_add+0x64/0x1a0
[  134.222399]  ? cifs_put_tcon+0x171/0x340 [cifs]
[  134.222772]  d_lru_add+0x44/0x60
[  134.222997]  dput+0x1fc/0x210
[  134.223213]  cifsFileInfo_put_final+0x11a/0x140 [cifs]
[  134.223576]  process_one_work+0x17c/0x320
[  134.223843]  worker_thread+0x188/0x280
[  134.224084]  ? __pfx_worker_thread+0x10/0x10
[  134.224366]  kthread+0xcc/0x100
[  134.224576]  ? __pfx_kthread+0x10/0x10
[  134.224827]  ret_from_fork+0x30/0x50
[  134.225063]  ? __pfx_kthread+0x10/0x10
[  134.225328]  ret_from_fork_asm+0x1b/0x30

This can be reproduce by following:
unshare -n bash -c "
mkdir -p ${CIFS_MNT}
ip netns attach root 1
ip link add eth0 type veth peer veth0 netns root
ip link set eth0 up
ip -n root link set veth0 up
ip addr add 192.168.0.2/24 dev eth0
ip -n root addr add 192.168.0.1/24 dev veth0
ip route add default via 192.168.0.1 dev eth0
ip netns exec root sysctl net.ipv4.ip_forward=1
ip netns exec root iptables -t nat -A POSTROUTING -s 192.168.0.2 -o
${DEV} -j MASQUERADE
mount -t cifs ${CIFS_PATH} ${CIFS_MNT} -o
vers=3.0,sec=ntlmssp,credentials=${CIFS_CRED},rsize=65536,wsize=65536,cache=none,echo_interval=1
touch ${CIFS_MNT}/a.txt
ip netns exec root iptables -t nat -D POSTROUTING -s 192.168.0.2 -o
${DEV} -j MASQUERADE
"
umount ${CIFS_MNT}

## References
- https://git.kernel.org/stable/c/21303c4a2b7275e626c6b67de0f45f2d5b9bb3e7
- https://git.kernel.org/stable/c/3baedc9b2f53e6a6ac57b16fdff0f9b954d9ca71
- https://git.kernel.org/stable/c/4465ebe67d89345954bb3622b25dd13e06f9d367
- https://git.kernel.org/stable/c/55fb9581986141659002264fdc75cef307811eb8
- https://git.kernel.org/stable/c/6d9a4aaaa8b2612b5ef9d581e2f286a458b71ee1
- https://git.kernel.org/stable/c/7839f1817a0cb6c4ed5cfe25d04845c43380a129
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74259.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74259
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
