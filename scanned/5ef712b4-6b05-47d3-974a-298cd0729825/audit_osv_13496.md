# [H] CVE-2018-20022

## Summary
Severity: High
Advisory: CVE-2018-20022
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-19
Source: https://osv.dev/vulnerability/CVE-2018-20022
Type: osv

## Details
LibVNC before 2f5b2ad1c6c99b1ac6482c95844a84d66bb52838 contains multiple weaknesses CWE-665: Improper Initialization vulnerability in VNC client code that allows attacker to read stack memory and can be abuse for information disclosure. Combined with another vulnerability, it can be used to leak stack memory layout and in bypassing ASLR

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00042.html
- https://lists.debian.org/debian-lts-announce/2019/11/msg00033.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00028.html
- https://usn.ubuntu.com/4547-1/
- https://usn.ubuntu.com/4547-2/
- https://usn.ubuntu.com/4587-1/
- https://ics-cert.kaspersky.com/advisories/klcert-advisories/2018/12/19/klcert-18-032-libvnc-multiple-memory-leaks/
- https://lists.debian.org/debian-lts-announce/2018/12/msg00017.html
- https://security.gentoo.org/glsa/201908-05
- https://security.gentoo.org/glsa/202006-06
- https://usn.ubuntu.com/3877-1/
- https://www.debian.org/security/2019/dsa-4383
