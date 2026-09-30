# [M] CVE-2020-26570

## Summary
Severity: Medium
Advisory: CVE-2020-26570
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-26570
Type: osv

## Details
The Oberthur smart card software driver in OpenSC before 0.21.0-rc1 has a heap-based buffer overflow in sc_oberthur_read_file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EXOHFDMNMO6IDECAGUTB3SJGAGXVRT6S/
- http://www.openwall.com/lists/oss-security/2020/11/24/4
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=24316
- https://lists.debian.org/debian-lts-announce/2021/11/msg00027.html
- https://github.com/OpenSC/OpenSC/commit/6903aebfddc466d966c7b865fae34572bf3ed23e
