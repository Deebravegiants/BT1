# [H] Pillow Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-8ghj-p4vj-mr35
CVE: CVE-2023-44271
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-03
Source: https://github.com/advisories/GHSA-8ghj-p4vj-mr35
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <10.0.0

## Details
An issue was discovered in Pillow before 10.0.0. It is a Denial of Service that uncontrollably allocates memory to process a given task, potentially causing a service to crash by having it run out of memory. This occurs for truetype in ImageFont when textlength in an ImageDraw instance operates on a long text argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44271
- https://github.com/python-pillow/Pillow/pull/7244
- https://github.com/python-pillow/Pillow/commit/1fe1bb49c452b0318cad12ea9d97c3bef188e9a7
- https://devhub.checkmarx.com/cve-details/CVE-2023-44271
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2023-227.yaml
- https://github.com/python-pillow/Pillow
- https://lists.debian.org/debian-lts-announce/2024/03/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N2JOEDUJDQLCUII2LQYZYSM7RJL2I3P4
