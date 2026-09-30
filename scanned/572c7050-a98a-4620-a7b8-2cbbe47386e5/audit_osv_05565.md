# [H] BIT-golang-2020-16845

## Summary
Severity: High
Advisory: BIT-golang-2020-16845
Aliases: CVE-2020-16845, GHSA-q6gq-997w-f55g, GO-2021-0142
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2020-16845
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.14.0 <1.14.7

## Details
Go before 1.13.15 and 14.x before 1.14.7 can have an infinite read loop in ReadUvarint and ReadVarint in encoding/binary via invalid inputs.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00030.html
- https://groups.google.com/forum/#%21topic/golang-announce/NyPIaucMgXo
- https://groups.google.com/forum/#%21topic/golang-announce/_ulYYcIWg3Q
- https://lists.debian.org/debian-lts-announce/2020/11/msg00037.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00038.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6RCFJTMKHY5ICGEM5BUFUEDDGSPJ25XU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KWRBAH4UZJO3RROQ72SYCUPFCJFA22FO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TACQFZDPA7AUR6TRZBCX2RGRFSDYLI7O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WV2VWKFTH4EJGZBZALVUJQJOAQB5MDQ4/
- https://security.netapp.com/advisory/ntap-20200924-0002/
- https://www.debian.org/security/2021/dsa-4848
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-16845
