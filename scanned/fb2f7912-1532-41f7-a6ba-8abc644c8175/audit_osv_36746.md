# [M] WeKan < 8.19 Checklist Deletion IDOR via Missing Relationship Validation

## Summary
Severity: Medium
Advisory: CVE-2026-25564
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-02-07
Source: https://osv.dev/vulnerability/CVE-2026-25564
Type: osv

## Details
WeKan versions prior to 8.19 contain an insecure direct object reference (IDOR) in checklist creation and related checklist routes. The implementation does not verify that the supplied cardId belongs to the supplied boardId, allowing cross-board ID tampering by manipulating identifiers.

## References
- https://wekan.fi/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25564.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25564
- https://www.vulncheck.com/advisories/wekan-checklist-deletion-idor-via-missing-relationship-validation
- https://github.com/wekan/wekan/commit/08a6f084eba09487743a7c807fb4a9000fcfa9ac
- https://github.com/wekan/wekan
