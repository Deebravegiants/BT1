# [M] CVE-2018-19840

## Summary
Severity: Medium
Advisory: CVE-2018-19840
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/CVE-2018-19840
Type: osv

## Details
The function WavpackPackInit in pack_utils.c in libwavpack.a in WavPack through 5.1.0 allows attackers to cause a denial-of-service (resource exhaustion caused by an infinite loop) via a crafted wav audio file because WavpackSetConfiguration64 mishandles a sample rate of zero.

## References
- http://packetstormsecurity.com/files/155743/Slackware-Security-Advisory-wavpack-Updates.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00013.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3BLSOEVEKF4VNNVNZ2AN46BJUT4TGVWT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CFFFWIWALGQPKINRDW3PRGRD5LOLGZA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BRWQNE3TH5UF64IKHKKHVCHJHUOVKJUH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NZGXJUHCGQI6XKLCBUZHXPYIIWMFWA22/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WVVKOBJR5APOB3KWUWJ4UWQHUBZQL6C6/
- https://seclists.org/bugtraq/2019/Dec/37
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00029.html
- https://github.com/dbry/WavPack/issues/53
- https://security.gentoo.org/glsa/202007-19
- https://usn.ubuntu.com/3839-1/
- https://github.com/dbry/WavPack/commit/070ef6f138956d9ea9612e69586152339dbefe51
