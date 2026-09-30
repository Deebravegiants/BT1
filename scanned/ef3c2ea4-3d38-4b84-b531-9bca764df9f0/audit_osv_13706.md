# [H] CVE-2018-21247

## Summary
Severity: High
Advisory: CVE-2018-21247
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/CVE-2018-21247
Type: osv

## Details
An issue was discovered in LibVNCServer before 0.9.13. There is an information leak (of uninitialized memory contents) in the libvncclient/rfbproto.c ConnectToRFBRepeater function.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4F6FUH4EFK4NAP6GT4TQRTBKWIRCZLIY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NVP7TJVYJDXDFRHVQ3ENEN3H354QPXEZ/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00066.html
- https://github.com/LibVNC/libvncserver/issues/253
- https://cert-portal.siemens.com/productcert/pdf/ssa-390195.pdf
- https://github.com/LibVNC/libvncserver/compare/LibVNCServer-0.9.12...LibVNCServer-0.9.13
