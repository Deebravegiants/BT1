# [M] CVE-2020-26571

## Summary
Severity: Medium
Advisory: CVE-2020-26571
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-26571
Type: osv

## Details
The gemsafe GPK smart card software driver in OpenSC before 0.21.0-rc1 has a stack-based buffer overflow in sc_pkcs15emu_gemsafeGPK_init.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EXOHFDMNMO6IDECAGUTB3SJGAGXVRT6S/
- http://www.openwall.com/lists/oss-security/2020/11/24/4
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=20612
- https://lists.debian.org/debian-lts-announce/2021/11/msg00027.html
