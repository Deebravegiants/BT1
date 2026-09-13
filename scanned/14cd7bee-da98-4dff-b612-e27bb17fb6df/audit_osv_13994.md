# [H] CVE-2018-6307

## Summary
Severity: High
Advisory: CVE-2018-6307
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-19
Source: https://osv.dev/vulnerability/CVE-2018-6307
Type: osv

## Details
LibVNC before commit ca2a5ac02fbbadd0a21fabba779c1ea69173d10b contains heap use-after-free vulnerability in server code of file transfer extension that can result remote code execution.

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00042.html
- https://github.com/LibVNC/libvncserver/issues/241
- https://ics-cert.kaspersky.com/advisories/klcert-advisories/2018/12/19/klcert-18-026-libvnc-heap-use-after-free/
- https://lists.debian.org/debian-lts-announce/2018/12/msg00017.html
- https://usn.ubuntu.com/3877-1/
- https://www.debian.org/security/2019/dsa-4383
