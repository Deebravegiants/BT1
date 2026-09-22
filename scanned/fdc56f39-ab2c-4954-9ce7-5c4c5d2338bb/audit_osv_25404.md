# [M] Metersphere missing permission check

## Summary
Severity: Medium
Advisory: CVE-2023-35937
Aliases: GHSA-7xj3-qrx5-524r
CVSS: 6.0 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:L)
Published: 2023-07-06
Source: https://osv.dev/vulnerability/CVE-2023-35937
Type: osv

## Details
Metersphere is an open source continuous testing platform. In versions prior to 2.10.2 LTS, some key APIs in Metersphere lack permission checks. This allows ordinary users to execute APIs that can only be executed by space administrators or project administrators. For example, ordinary users can be updated as space administrators. Version 2.10.2 LTS has a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35937.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-7xj3-qrx5-524r
- https://nvd.nist.gov/vuln/detail/CVE-2023-35937
