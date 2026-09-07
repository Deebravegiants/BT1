# [M] Apache Superset: Error verbosity exposes metadata in analytics databases

## Summary
Severity: Medium
Advisory: GHSA-2cx9-54hp-r698
CVE: CVE-2024-53948
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-2cx9-54hp-r698
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <4.1.0

## Details
Generation of Error Message Containing analytics metadata Information in Apache Superset.

This issue affects Apache Superset: before 4.1.0.

Users are recommended to upgrade to version 4.1.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53948
- https://github.com/apache/superset/commit/ac3a10d8f192520580b8ce545cf418dc7928d27c
- https://github.com/apache/superset
- https://lists.apache.org/thread/8howpf3png0wrgpls46ggk441oczlfvf
- http://www.openwall.com/lists/oss-security/2024/12/09/3
