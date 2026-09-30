# [M] InvenTree Plugin Installation - Insufficient Permissions

## Summary
Severity: Medium
Advisory: CVE-2026-35479
Aliases: GHSA-7c3q-vwcv-2vp7
CVSS: 6.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-35479
Type: osv

## Details
InvenTree is an Open Source Inventory Management System. Prior to 1.2.7 and 1.3.0, any users who have staff access permissions can install plugins via the API, without requiring "superuser" account access. This level of permission requirement is out of alignment with other plugin actions (such as uninstalling) which do require superuser access. The vulnerability allows staff users (who may be considered to have a lower level of trust than a superuser account) to install arbitrary (and potentially harmful) plugins. This vulnerability is fixed in 1.2.7 and 1.3.0.

## References
- https://docs.inventree.org/en/stable/concepts/threat_model/#assumed-trust
- https://docs.inventree.org/en/stable/start/config/#plugin-options
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35479.json
- https://github.com/inventree/InvenTree/security/advisories/GHSA-7c3q-vwcv-2vp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35479
