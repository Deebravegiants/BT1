# [C] CVE-2018-15126

## Summary
Severity: Critical
Advisory: CVE-2018-15126
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-19
Source: https://osv.dev/vulnerability/CVE-2018-15126
Type: osv

## Details
LibVNC before commit 73cb96fec028a576a5a24417b57723b55854ad7b contains heap use-after-free vulnerability in server code of file transfer extension that can result remote code execution

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00042.html
- https://ics-cert.kaspersky.com/advisories/klcert-advisories/2018/12/19/klcert-18-027-libvnc-heap-use-after-free/
- https://lists.debian.org/debian-lts-announce/2019/01/msg00029.html
- https://usn.ubuntu.com/3877-1/
- https://www.debian.org/security/2019/dsa-4383
