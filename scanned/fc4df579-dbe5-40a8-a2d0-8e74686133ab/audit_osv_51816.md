# [H] CVE-2021-41054

## Summary
Severity: High
Advisory: CVE-2021-41054
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-41054
Type: osv

## Details
tftpd_file.c in atftp through 0.7.4 has a buffer overflow because buffer-size handling does not properly consider the combination of data, OACK, and other options.

## References
- https://lists.debian.org/debian-lts-announce/2021/11/msg00014.html
- https://sourceforge.net/p/atftp/code/ci/d255bf90834fb45be52decf9bc0b4fb46c90f205/
- https://github.com/nu11secur1ty/CVE-mitre/tree/main/CVE-2021-41054
