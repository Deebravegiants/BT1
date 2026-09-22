# [M] Apache Superset uncontrolled resource consumption

## Summary
Severity: Medium
Advisory: GHSA-95mg-jgfx-54v9
CVE: CVE-2023-46104
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-19
Source: https://github.com/advisories/GHSA-95mg-jgfx-54v9
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <2.1.2
- PyPI: `apache-superset` — affected >=3.0.0 <3.1.0rc1

## Details
Uncontrolled resource consumption can be triggered by authenticated attacker that uploads a malicious ZIP to import database, dashboards or datasets.  
This vulnerability exists in Apache Superset versions up to and including 2.1.2 and versions 3.0.0, 3.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46104
- https://github.com/apache/superset/commit/7c23cb0b3fd224c320b35f05e74b572033569154
- https://github.com/apache/superset/commit/f473d13d0d89de5990209ff81b17dfe2cee884d3
- https://github.com/apache/superset
- https://lists.apache.org/thread/yxbxg4wryb7cb7wyybk11l5nqy0rsrvl
- http://www.openwall.com/lists/oss-security/2023/12/19/1
- http://www.openwall.com/lists/oss-security/2024/02/14/2
- http://www.openwall.com/lists/oss-security/2024/02/14/3
