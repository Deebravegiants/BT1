# [M] GLPI LDAP Injection during authentication

## Summary
Severity: Medium
Advisory: CVE-2023-51446
Aliases: GHSA-p995-jmfv-c7r8
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-01
Source: https://osv.dev/vulnerability/CVE-2023-51446
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package. When authentication is made against a LDAP, the authentication form can be used to perform LDAP injection. Upgrade to 10.0.12.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51446.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-p995-jmfv-c7r8
- https://nvd.nist.gov/vuln/detail/CVE-2023-51446
- https://github.com/glpi-project/glpi/commit/58c67d78f2e3ad08264213e9aaf56eab3c9ded35
