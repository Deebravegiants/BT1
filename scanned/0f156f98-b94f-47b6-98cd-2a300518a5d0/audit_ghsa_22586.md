# [M] Djblets Cross-site scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4xf6-xr96-7vmp
CVE: CVE-2014-3995
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4xf6-xr96-7vmp
Type: github-advisory

## Affected
- PyPI: `Djblets` — affected >=0 <0.7.30
- PyPI: `Djblets` — affected >=0.8 <0.8.3

## Details
A cross-site scripting (XSS) vulnerability in `gravatars/templatetags/gravatars.py` in Djblets before 0.7.30 and 0.8.x before 0.8.3 for Django allows remote attackers to inject arbitrary web script or HTML via a user display name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3995
- https://github.com/djblets/djblets/commit/50000d0bbb983fa8c097b588d06b64df8df483bd
- https://github.com/djblets/djblets/commit/77ac64642ad530bf69e390c51fc6fdcb8914c8e7
- https://github.com/djblets/djblets/commit/e2c79117efd925636acd871a5f473512602243cf
- https://github.com/djblets/djblets
- https://github.com/pypa/advisory-database/tree/main/vulns/djblets/PYSEC-2014-79.yaml
- https://web.archive.org/web/20140702014704/http://seclists.org/oss-sec/2014/q2/498
- https://web.archive.org/web/20140702025724/http://seclists.org/oss-sec/2014/q2/494
- http://seclists.org/oss-sec/2014/q2/494
- http://seclists.org/oss-sec/2014/q2/498
