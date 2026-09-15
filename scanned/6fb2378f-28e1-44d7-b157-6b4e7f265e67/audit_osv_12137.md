# [H] CVE-2018-10536

## Summary
Severity: High
Advisory: CVE-2018-10536
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/CVE-2018-10536
Type: osv

## Details
An issue was discovered in WavPack 5.1.0 and earlier. The WAV parser component contains a vulnerability that allows writing to memory because ParseRiffHeaderConfig in riff.c does not reject multiple format chunks.

## References
- http://packetstormsecurity.com/files/155743/Slackware-Security-Advisory-wavpack-Updates.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CFFFWIWALGQPKINRDW3PRGRD5LOLGZA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BRWQNE3TH5UF64IKHKKHVCHJHUOVKJUH/
- https://seclists.org/bugtraq/2019/Dec/37
- https://usn.ubuntu.com/3637-1/
- https://www.debian.org/security/2018/dsa-4197
- https://github.com/dbry/WavPack/issues/30
- https://github.com/dbry/WavPack/issues/31
- https://github.com/dbry/WavPack/issues/32
- https://github.com/dbry/WavPack/commit/26cb47f99d481ad9b93eeff80d26e6b63bbd7e15
