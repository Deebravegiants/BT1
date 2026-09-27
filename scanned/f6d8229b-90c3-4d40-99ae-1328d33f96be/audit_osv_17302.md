# [H] CVE-2020-14398

## Summary
Severity: High
Advisory: CVE-2020-14398
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/CVE-2020-14398
Type: osv

## Details
An issue was discovered in LibVNCServer before 0.9.13. An improperly closed TCP connection causes an infinite loop in libvncclient/sockets.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00066.html
- https://github.com/LibVNC/libvncserver/compare/LibVNCServer-0.9.12...LibVNCServer-0.9.13
- https://usn.ubuntu.com/4434-1/
- https://cert-portal.siemens.com/productcert/pdf/ssa-390195.pdf
- https://github.com/LibVNC/libvncserver/commit/57433015f856cc12753378254ce4f1c78f5d9c7b
