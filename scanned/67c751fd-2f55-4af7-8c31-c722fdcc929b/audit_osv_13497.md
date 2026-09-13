# [H] CVE-2018-20023

## Summary
Severity: High
Advisory: CVE-2018-20023
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-19
Source: https://osv.dev/vulnerability/CVE-2018-20023
Type: osv

## Details
LibVNC before 8b06f835e259652b0ff026898014fc7297ade858 contains CWE-665: Improper Initialization vulnerability in VNC Repeater client code that allows attacker to read stack memory and can be abuse for information disclosure. Combined with another vulnerability, it can be used to leak stack memory layout and in bypassing ASLR

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00042.html
- https://usn.ubuntu.com/4547-1/
- https://usn.ubuntu.com/4587-1/
- https://ics-cert.kaspersky.com/advisories/klcert-advisories/2018/12/19/klcert-18-033-libvnc-memory-leak/
- https://lists.debian.org/debian-lts-announce/2018/12/msg00017.html
- https://security.gentoo.org/glsa/201908-05
- https://usn.ubuntu.com/3877-1/
- https://www.debian.org/security/2019/dsa-4383
