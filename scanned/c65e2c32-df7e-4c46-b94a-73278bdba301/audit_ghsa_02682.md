# [H] XML External Entity Injection in PyWPS

## Summary
Severity: High
Advisory: GHSA-p9wf-3xpg-c9g5
CVE: CVE-2021-39371
CWE: CWE-611, CWE-91
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-p9wf-3xpg-c9g5
Type: github-advisory

## Affected
- PyPI: `pywps` — affected >=0 <4.5.0

## Details
An XML external entity (XXE) injection in PyWPS before 4.5.0 allows an attacker to view files on the application server filesystem by assigning a path to the entity. OWSLib 0.24.1 may also be affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39371
- https://github.com/geopython/OWSLib/issues/790
- https://github.com/geopython/pywps/pull/616
- https://github.com/geopython/pywps/commit/7d6b26a2e931df2feca0b7fb24f4d01610825aee
- https://github.com/advisories/GHSA-p9wf-3xpg-c9g5
- https://github.com/geopython/pywps
- https://github.com/pypa/advisory-database/tree/main/vulns/pywps/PYSEC-2021-121.yaml
- https://lists.debian.org/debian-lts-announce/2021/09/msg00001.html
