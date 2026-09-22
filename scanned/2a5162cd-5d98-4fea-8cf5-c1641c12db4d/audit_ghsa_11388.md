# [M] mppx has Stripe charge credential replay via missing idempotency check

## Summary
Severity: Medium
Advisory: GHSA-8mhj-rffc-rcvw
CVE: CVE-2026-34210
CWE: CWE-697
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-8mhj-rffc-rcvw
Type: github-advisory

## Affected
- npm: `mppx` — affected >=0 <0.4.11

## Details
### Impact

The `stripe/charge` payment method did not check Stripe's `Idempotent-Replayed` response header when creating PaymentIntents. An attacker could replay a valid credential containing the same `spt` token against a new challenge, and the server would accept the replayed Stripe PaymentIntent as a new successful payment without actually charging the customer again. This allowed an attacker to pay once and consume unlimited resources by replaying the credential.

### Patches

Fixed in 0.4.11. The server now checks the `Idempotent-Replayed` header and rejects replayed PaymentIntents.

### Workarounds

There are no workarounds available for this vulnerability.

## References
- https://github.com/wevm/mppx/security/advisories/GHSA-8mhj-rffc-rcvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-34210
- https://github.com/wevm/mppx/commit/b2b1a0b60506fc71aa80b8a025084949dca1a994
- https://github.com/wevm/mppx
- https://github.com/wevm/mppx/releases/tag/mppx%400.4.11
- https://github.com/wevm/mppx/releases/tag/mppx@0.4.11
