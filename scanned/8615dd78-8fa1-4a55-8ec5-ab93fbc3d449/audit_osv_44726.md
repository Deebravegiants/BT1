# [M] potpie through 2.0.0 Missing Ownership Check via code-changes sync

## Summary
Severity: Medium
Advisory: CVE-2026-85669
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85669
Type: osv

## Details
potpie through 2.0.0 fails to verify user ownership on the POST /conversations/{conversation_id}/code-changes/sync endpoint. Authenticated attackers can write arbitrary file changes into other users' conversations by supplying their conversation IDs, allowing unauthorized modification of pending changes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85669.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85669
- https://www.vulncheck.com/advisories/potpie-through-2.0.0-missing-ownership-check-via-code-changes-sync
- https://github.com/potpie-ai/potpie/issues/870
- https://github.com/potpie-ai/potpie
- https://github.com/potpie-ai/potpie/blob/v2.0.0/legacy/app/modules/conversations/conversations_router.py
