# [M] CVE-2019-18809

## Summary
Severity: Medium
Advisory: CVE-2019-18809
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18809
Type: osv

## Details
A memory leak in the af9005_identify_state() function in drivers/media/usb/dvb-usb/af9005.c in the Linux kernel through 5.3.9 allows attackers to cause a denial of service (memory consumption), aka CID-2289adbfa559.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWWOOJKZ4NQYN4RMFIVJ3ZIXKJJI3MKP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LYIFGYEDQXP5DVJQQUARQRK2PXKBKQGY/
- https://usn.ubuntu.com/4287-1/
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4285-1/
- https://usn.ubuntu.com/4287-2/
- https://usn.ubuntu.com/4300-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://github.com/torvalds/linux/commit/2289adbfa559050d2a38bcd9caac1c18b800e928
