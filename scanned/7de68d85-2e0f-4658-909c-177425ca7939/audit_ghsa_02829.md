# [H] Cobbler before 3.3.0 allows log poisoning

## Summary
Severity: High
Advisory: GHSA-cpqf-3c3r-c9g2
CVE: CVE-2021-40323
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-05
Source: https://github.com/advisories/GHSA-cpqf-3c3r-c9g2
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <3.3.0

## Details
Cobbler before 3.3.0 allows log poisoning, and resultant Remote Code Execution, via an XMLRPC method that logs to the logfile for template injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40323
- https://github.com/cobbler/cobbler/commit/d8f60bbf14a838c8c8a1dba98086b223e35fe70a
- https://github.com/advisories/GHSA-cpqf-3c3r-c9g2
- https://github.com/cobbler/cobbler
- https://github.com/cobbler/cobbler/releases/tag/v3.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/cobbler/PYSEC-2021-373.yaml
