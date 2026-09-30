# [C] Mercurial Incorrect Access Control vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4mr4-7vjv-9hm6
CVE: CVE-2018-1000132
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4mr4-7vjv-9hm6
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <4.5.1

## Details
Mercurial version 4.5 and earlier contains a Incorrect Access Control (CWE-285) vulnerability in Protocol server that can result in Unauthorized data access. This attack appear to be exploitable via network connectivity. This vulnerability appears to have been fixed in 4.5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000132
- https://access.redhat.com/errata/RHSA-2019:2276
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2018-87.yaml
- https://lists.debian.org/debian-lts-announce/2018/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00005.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00032.html
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_4.5.1_.2F_4.5.2_.282018-03-06.29
