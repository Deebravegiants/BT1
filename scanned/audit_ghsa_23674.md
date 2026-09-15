# [H] Kallithea CRLF injection vulnerability

## Summary
Severity: High
Advisory: GHSA-vfg9-phjp-9frw
CVE: CVE-2015-5285
CWE: CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vfg9-phjp-9frw
Type: github-advisory

## Affected
- PyPI: `kallithea` — affected >=0 <0.3

## Details
CRLF injection vulnerability in Kallithea before 0.3 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via the `came_from` parameter to `_admin/login`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5285
- https://github.com/NexMirror/Kallithea
- https://github.com/pypa/advisory-database/tree/main/vulns/kallithea/PYSEC-2015-13.yaml
- https://kallithea-scm.org/security/cve-2015-5285.html
- https://www.exploit-db.com/exploits/38424
- http://packetstormsecurity.com/files/133897/Kallithea-0.2.9-HTTP-Response-Splitting.html
- http://www.zeroscience.mk/en/vulnerabilities/ZSL-2015-5267.php
