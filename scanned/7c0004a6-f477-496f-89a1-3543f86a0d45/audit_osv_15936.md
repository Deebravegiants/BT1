# [H] CVE-2019-20840

## Summary
Severity: High
Advisory: CVE-2019-20840
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/CVE-2019-20840
Type: osv

## Details
An issue was discovered in LibVNCServer before 0.9.13. libvncserver/ws_decode.c can lead to a crash because of unaligned accesses in hybiReadAndDecode.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4F6FUH4EFK4NAP6GT4TQRTBKWIRCZLIY/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00066.html
- https://github.com/LibVNC/libvncserver/compare/LibVNCServer-0.9.12...LibVNCServer-0.9.13
- https://usn.ubuntu.com/4434-1/
- https://cert-portal.siemens.com/productcert/pdf/ssa-390195.pdf
- https://github.com/LibVNC/libvncserver/commit/0cf1400c61850065de590d403f6d49e32882fd76
