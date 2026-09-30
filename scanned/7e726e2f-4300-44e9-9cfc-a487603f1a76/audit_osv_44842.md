# [M] Snipe-IT 8.6.3 Race Condition via Consumable Checkout

## Summary
Severity: Medium
Advisory: CVE-2026-86766
Aliases: GHSA-x4g2-87xc-m5jm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86766
Type: osv

## Details
Snipe-IT versions up to and including 8.6.3 contain a race condition (TOCTOU) in the consumable checkout API endpoint (POST /api/v1/consumables/{consumable_id}/checkout). The requested quantity is validated against the number of remaining units before the database transaction begins, and the transaction then creates the checkout records without locking the consumable row or re-checking availability. An authenticated user with permission to check out consumables can submit concurrent checkout requests for the same consumable so that both requests pass the availability check and succeed, over-allocating stock and driving the remaining inventory negative (e.g., a consumable with 1 remaining unit ends at -1 after two concurrent 1-unit checkouts). The issue is fixed in 8.7.0, which re-fetches the parent row under lockForUpdate inside the transaction and re-validates availability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86766.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-x4g2-87xc-m5jm
- https://nvd.nist.gov/vuln/detail/CVE-2026-86766
- https://www.vulncheck.com/advisories/snipe-it-8.6.3-race-condition-via-consumable-checkout
- https://github.com/grokability/snipe-it/commit/f71806b1e0efbd3bc2b6be61994ad2a5d5d6c206
