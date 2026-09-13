# [M] Prevent topic list filtering by hidden tags for unauthorized users in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-45297
Aliases: CVE-2024-45297, GHSA-58xw-3qr3-53gp
Ecosystem: Bitnami
Published: 2024-10-11
Source: https://osv.dev/vulnerability/BIT-discourse-2024-45297
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.3.2

## Details
Discourse is an open source platform for community discussion. Users can see topics with a hidden tag if they know the label/name of that tag. This issue has been patched in the latest stable, beta and tests-passed version of Discourse. All users area are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-58xw-3qr3-53gp
- https://nvd.nist.gov/vuln/detail/CVE-2024-45297
