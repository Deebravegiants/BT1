# [H] GLPI contains an SQL injection through the saved searches

## Summary
Severity: High
Advisory: CVE-2024-29889
Aliases: GHSA-8xvf-v6vv-r75g
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-05-07
Source: https://osv.dev/vulnerability/CVE-2024-29889
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package. Prior to 10.0.15, an authenticated user can exploit a SQL injection vulnerability in the saved searches feature to alter another user account data take control of it. This vulnerability is fixed in 10.0.15.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29889.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-8xvf-v6vv-r75g
- https://nvd.nist.gov/vuln/detail/CVE-2024-29889
- https://github.com/glpi-project/glpi/commit/0a6b28be4c0f848106c60b554c703ec2e178d6c7
