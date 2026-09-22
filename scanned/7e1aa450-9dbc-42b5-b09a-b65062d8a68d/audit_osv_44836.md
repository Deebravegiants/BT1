# [M] Snipe-IT before 8.7.0 Information Disclosure via Custom Fields

## Summary
Severity: Medium
Advisory: CVE-2026-86757
Aliases: GHSA-j36v-ghpr-m963
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86757
Type: osv

## Details
Snipe-IT before 8.7.0 fails to properly gate access to encrypted custom-field values in asset form templates for listbox, textarea, markdown-textarea, and date/datetime picker elements. Authenticated users with assets.edit, assets.checkin, assets.checkout, or assets.audit permissions can read plaintext encrypted custom field values by opening asset forms, bypassing the assets.view.encrypted_custom_fields permission check.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86757.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-j36v-ghpr-m963
- https://nvd.nist.gov/vuln/detail/CVE-2026-86757
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-information-disclosure-via-custom-fields
