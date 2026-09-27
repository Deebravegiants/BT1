# [M] CVE-2019-11498

## Summary
Severity: Medium
Advisory: CVE-2019-11498
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-11498
Type: osv

## Details
WavpackSetConfiguration64 in pack_utils.c in libwavpack.a in WavPack through 5.1.0 has a "Conditional jump or move depends on uninitialised value" condition, which might allow attackers to cause a denial of service (application crash) via a DFF file that lacks valid sample-rate data.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CFFFWIWALGQPKINRDW3PRGRD5LOLGZA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BRWQNE3TH5UF64IKHKKHVCHJHUOVKJUH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NZDKXGA2ZNSSM64ZYDHOWCO4Q4VAKAON/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SCK2YJXY6V5CKGKSF2PPN7RL2DXVOC6G/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00013.html
- https://security.gentoo.org/glsa/202007-19
- https://usn.ubuntu.com/3960-1/
- https://github.com/dbry/WavPack/issues/67
- https://github.com/dbry/WavPack/commit/bc6cba3f552c44565f7f1e66dc1580189addb2b4
