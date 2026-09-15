# [C] Gevent allows remote attacker to escalate privileges

## Summary
Severity: Critical
Advisory: GHSA-x7m3-jprg-wc5g
CVE: CVE-2023-41419
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-25
Source: https://github.com/advisories/GHSA-x7m3-jprg-wc5g
Type: github-advisory

## Affected
- PyPI: `gevent` — affected >=0 <23.9.0

## Details
An issue in Gevent before version 23.9.0 allows a remote attacker to escalate privileges via a crafted script to the WSGIServer component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41419
- https://github.com/gevent/gevent/issues/1989
- https://github.com/gevent/gevent/commit/2f53c851eaf926767fbac62385615efd4886221c
- https://github.com/gevent/gevent
- https://github.com/pypa/advisory-database/tree/main/vulns/gevent/PYSEC-2023-177.yaml
- https://lists.debian.org/debian-lts-announce/2025/11/msg00020.html
- http://www.gevent.org/changelog.html
