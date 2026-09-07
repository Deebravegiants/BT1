# [M] Apache Superset has Incorrect Default Permissions

## Summary
Severity: Medium
Advisory: GHSA-vv65-fjfj-4736
CVE: CVE-2023-42501
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-vv65-fjfj-4736
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <2.1.2

## Details
Unnecessary read permissions within the Gamma role would allow authenticated users to read configured CSS templates and annotations.
This issue affects Apache Superset: before 2.1.2.
Users should upgrade to version or above 2.1.2 and run `superset init` to reconstruct the Gamma role or remove `can_read` permission from the mentioned resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42501
- https://github.com/apache/superset
- https://lists.apache.org/thread/vk1rmrh9kz0chjmc9tk7o3md6zpz4ygh
- http://www.openwall.com/lists/oss-security/2023/11/27/3
