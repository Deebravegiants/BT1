# [H] CVE-2021-42716

## Summary
Severity: High
Advisory: CVE-2021-42716
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-10-21
Source: https://osv.dev/vulnerability/CVE-2021-42716
Type: osv

## Details
An issue was discovered in stb stb_image.h 2.27. The PNM loader incorrectly interpreted 16-bit PGM files as 8-bit when converting to RGBA, leading to a buffer overflow when later reinterpreting the result as a 16-bit buffer. An attacker could potentially have crashed a service using stb_image, or read up to 1024 bytes of non-consecutive heap data without control over the read location.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3TDGZFLBOP27LZKLH45WQLSNPSPP7S7Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AF2CNP4FVC6LDKNOO4WDCGNDYIP3MPK6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FTZXHFZD36BGE5P6JF252NZZLKMGCY4T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VP2YEXEAJWI76FPM7D7VXHWD3WESQEYC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEGXBDEMTFGINETMJENBZ6SCHVEJQJSY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CI23LXPEV2GCDQTJSKO6CIILBDTI3R42/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G2M5CRSGPRF7G3YB5CLU4FXW7ANNHAYT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ID6II3RIKAMVGVMC6ZAQIXXYYDMTVC4N/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TXX76TJMZBPN3NU542MGN6B7C7QHRFGB/
- https://github.com/nothings/stb/pull/1223
- https://github.com/nothings/stb/issues/1166
- https://github.com/nothings/stb/issues/1225
