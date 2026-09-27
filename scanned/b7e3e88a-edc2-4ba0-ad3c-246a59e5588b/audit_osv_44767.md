# [M] BookWyrm through 0.9.1 Insecure Direct Object Reference in EditStatus Exposes Followers-Only and Direct Statuses

## Summary
Severity: Medium
Advisory: CVE-2026-86111
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86111
Type: osv

## Details
BookWyrm through 0.9.1 fails to validate user visibility permissions in the status edit endpoint, allowing authenticated attackers to read followers-only and direct-message reviews by enumerating sequential status IDs. Attackers can access the raw content of restricted statuses through the edit view, bypassing the privacy protections documented for these message types.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86111
- https://www.vulncheck.com/advisories/bookwyrm-through-0.9.1-insecure-direct-object-reference-in-editstatus-exposes-followers-only-and-direct-statuses
- https://github.com/bookwyrm-social/bookwyrm
- https://github.com/bookwyrm-social/bookwyrm/blob/v0.9.1/bookwyrm/templates/snippets/create_status/content_field.html
- https://github.com/bookwyrm-social/bookwyrm/blob/v0.9.1/bookwyrm/views/status.py
- https://github.com/geo-chen/oss/blob/main/bookwyrm.md#finding-1-authenticated-idor-in-editstatus-exposes-private-review-comment-and-quotation-content
