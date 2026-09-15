# [M] CVE-2020-35738

## Summary
Severity: Medium
Advisory: CVE-2020-35738
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-35738
Type: osv

## Details
WavPack 5.3.0 has an out-of-bounds write in WavpackPackSamples in pack_utils.c because of an integer overflow in a malloc argument. NOTE: some third-parties claim that there are later "unofficial" releases through 5.3.2, which are also affected.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2YZLKYE66EU4XRHTABV5LB2G7ZDZ422F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/76B7K6F74FDQATG7FECXR5KPIG52O2VL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PENN4ZXRPZULEJOYTTLUZMBZ5H46QTUC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VDFY4NGGDUTLVID5PNVU7LL2G2ZJLZFY/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00013.html
- https://github.com/dbry/WavPack/issues/91
