# [M] CVE-2018-19841

## Summary
Severity: Medium
Advisory: CVE-2018-19841
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/CVE-2018-19841
Type: osv

## Details
The function WavpackVerifySingleBlock in open_utils.c in libwavpack.a in WavPack through 5.1.0 allows attackers to cause a denial-of-service (out-of-bounds read and application crash) via a crafted WavPack Lossless Audio file, as demonstrated by wvunpack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3BLSOEVEKF4VNNVNZ2AN46BJUT4TGVWT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CFFFWIWALGQPKINRDW3PRGRD5LOLGZA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BRWQNE3TH5UF64IKHKKHVCHJHUOVKJUH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NZGXJUHCGQI6XKLCBUZHXPYIIWMFWA22/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WVVKOBJR5APOB3KWUWJ4UWQHUBZQL6C6/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00029.html
- http://packetstormsecurity.com/files/155743/Slackware-Security-Advisory-wavpack-Updates.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00013.html
- https://seclists.org/bugtraq/2019/Dec/37
- https://security.gentoo.org/glsa/202007-19
- https://usn.ubuntu.com/3839-1/
- https://github.com/dbry/WavPack/commit/bba5389dc598a92bdf2b297c3ea34620b6679b5b
- https://github.com/dbry/WavPack/issues/54
