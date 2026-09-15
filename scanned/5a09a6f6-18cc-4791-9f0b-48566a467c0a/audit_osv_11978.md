# [C] CVE-2018-1000517

## Summary
Severity: Critical
Advisory: CVE-2018-1000517
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000517
Type: osv

## Details
BusyBox project BusyBox wget version prior to commit 8e2174e9bd836e53c8b9c6e00d1bc6e2a718686e contains a Buffer Overflow vulnerability in Busybox wget that can result in heap buffer overflow. This attack appear to be exploitable via network connectivity. This vulnerability appears to have been fixed in after commit 8e2174e9bd836e53c8b9c6e00d1bc6e2a718686e.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00037.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00020.html
- https://usn.ubuntu.com/3935-1/
- https://git.busybox.net/busybox/commit/?id=8e2174e9bd836e53c8b9c6e00d1bc6e2a718686e
