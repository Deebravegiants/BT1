# [M] Apache StreamPipes has improper privilege management in a REST interface

## Summary
Severity: Medium
Advisory: GHSA-vm7w-2724-5m23
CVE: CVE-2024-24778
CWE: CWE-269
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-vm7w-2724-5m23
Type: github-advisory

## Affected
- Maven: `org.apache.streampipes:streampipes-parent` — affected >=0 <0.97.0
- PyPI: `streampipes` — affected >=0 <0.97.0

## Details
Improper privilege management in a REST interface allowed registered users to access unauthorized resources if the resource ID was known. 

This issue affects Apache StreamPipes: through 0.95.1.

Users are recommended to upgrade to version 0.97.0 which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24778
- https://github.com/apache/streampipes
- https://github.com/pypa/advisory-database/tree/main/vulns/streampipes/PYSEC-2025-66.yaml
- https://lists.apache.org/thread/j14w6wghlwwrgfgc6hoz9f94fwxtlgzh
- http://www.openwall.com/lists/oss-security/2025/03/03/1
