# [M] monetr: Protected Transactions Deletable via PUT

## Summary
Severity: Medium
Advisory: GHSA-hqxq-hwqf-wg83
CVE: CVE-2026-39901
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-hqxq-hwqf-wg83
Type: github-advisory

## Affected
- Go: `github.com/monetr/monetr` — affected >=0 <1.12.3

## Details
### Summary
A transaction integrity flaw allows an authenticated tenant user to soft-delete synced non-manual transactions through the transaction update endpoint, despite the application explicitly blocking deletion of those transactions via the normal `DELETE` path. This bypass undermines the intended protection for imported transaction records and allows protected transactions to be hidden from normal views.

### Details
The issue affects the transaction update path for synced transactions associated with non-manual links. The intended policy is clearly enforced in the `DELETE` handler: deletion of synced transactions for non-manual links is rejected with an error indicating that such transactions cannot be deleted.

However, the `PUT` update path still accepts a client-controlled full `Transaction` object and persists fields that should be server-managed, including `deletedAt`. The update logic appears to restrict only selected fields, which leaves `deletedAt` attacker-controllable.

Verified behavior on the same synced transaction showed:

- `DELETE` was denied with the expected protection error for non-manual links
- `PUT` with a user-supplied `deletedAt` value succeeded and returned `200 OK`
- a subsequent transaction list no longer showed the transaction
- `GET` by transaction ID still returned the record with `deletedAt` populated

This demonstrates a policy bypass: although the server explicitly defines synced transactions on non-manual links as non-deletable through the dedicated delete route, the same outcome can still be achieved through the update route by setting the soft-delete field directly.

The vulnerability is therefore not a simple UI inconsistency. It is a server-side authorization and integrity flaw caused by trusting a client-supplied full transaction object and failing to protect sensitive server-managed fields from modification.

### PoC
The issue can be reproduced by identifying a synced transaction on a non-manual link, confirming that the normal `DELETE` route rejects deletion, then submitting an update request that sets the transaction’s `deletedAt` field. The transaction will then disappear from normal listing views even though direct retrieval still shows the record as soft-deleted.

### Impact
- **Type:** Authorization bypass / integrity violation
- **Who is impacted:** Authenticated tenant users and any deployment relying on synced transaction immutability for non-manual links
- **Security impact:** Attackers can hide or effectively delete protected imported transactions that should not be deletable, compromising transaction history, bookkeeping integrity, and trust in audit-relevant server-managed fields
- **Attack preconditions:** The attacker must be authenticated and able to access a synced transaction within their own tenant/account scope

## References
- https://github.com/monetr/monetr/security/advisories/GHSA-hqxq-hwqf-wg83
- https://nvd.nist.gov/vuln/detail/CVE-2026-39901
- https://github.com/monetr/monetr
- https://github.com/monetr/monetr/releases/tag/v1.12.3
