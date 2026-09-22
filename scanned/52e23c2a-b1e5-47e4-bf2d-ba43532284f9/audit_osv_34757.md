# [M] GLPI vulnerable to unauthorized access to restricted Knowledge Base items through the API

## Summary
Severity: Medium
Advisory: CVE-2025-64520
Aliases: GHSA-62p9-prpq-j62q
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-64520
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 9.1.0 and prior to version 10.0.21, an unauthorized user with an API access can read all knowledge base entries. Users should upgrade to 10.0.21 to receive a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64520.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-62p9-prpq-j62q
- https://nvd.nist.gov/vuln/detail/CVE-2025-64520
- https://github.com/glpi-project/glpi/commit/a3d5cc4a63ae592c0b5592ebe6d562164904dab3
