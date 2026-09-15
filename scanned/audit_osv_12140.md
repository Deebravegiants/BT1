# [M] CVE-2018-10539

## Summary
Severity: Medium
Advisory: CVE-2018-10539
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/CVE-2018-10539
Type: osv

## Details
An issue was discovered in WavPack 5.1.0 and earlier for DSDiff input. Out-of-bounds writes can occur because ParseDsdiffHeaderConfig in dsdiff.c does not validate the sizes of unknown chunks before attempting memory allocation, related to a lack of integer-overflow protection within a bytes_to_copy calculation and subsequent malloc call, leading to insufficient memory allocation.

## References
- http://packetstormsecurity.com/files/155743/Slackware-Security-Advisory-wavpack-Updates.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CFFFWIWALGQPKINRDW3PRGRD5LOLGZA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BRWQNE3TH5UF64IKHKKHVCHJHUOVKJUH/
- https://seclists.org/bugtraq/2019/Dec/37
- https://usn.ubuntu.com/3637-1/
- https://www.debian.org/security/2018/dsa-4197
- https://github.com/dbry/WavPack/issues/33
- https://github.com/dbry/WavPack/commit/6f8bb34c2993a48ab9afbe353e6d0cff7c8d821d
