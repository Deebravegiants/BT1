# [M] GLPI's incomprehensive permission checks can lead to data removal from allowed users

## Summary
Severity: Medium
Advisory: CVE-2025-53112
Aliases: GHSA-rp7w-6343-3m2r
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-53112
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. In versions 9.1.0 through 10.0.18, a lack of permission checks can result in unauthorized removal of some specific resources. This is fixed in version 10.0.19.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53112.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-rp7w-6343-3m2r
- https://nvd.nist.gov/vuln/detail/CVE-2025-53112
