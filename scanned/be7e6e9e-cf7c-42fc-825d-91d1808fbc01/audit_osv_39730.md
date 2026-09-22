# [M] Ghostfolio has a Stripe subscription bypass

## Summary
Severity: Medium
Advisory: CVE-2026-47127
Aliases: GHSA-j465-x2w3-wjj8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-47127
Type: osv

## Details
Ghostfolio is an open source wealth management software. Prior to version 3.4.0, Ghostfolio's Stripe checkout success-URL handler at `GET /api/v1/subscription/stripe/callback?checkoutSessionId=<id>` retrieves the Stripe Checkout Session by ID and unconditionally grants a Premium subscription to the session's `client_reference_id` — without ever checking `session.payment_status` or `session.status`. There is no separate Stripe webhook endpoint with `stripe-signature` verification; this callback is the sole code path that creates Stripe-driven subscriptions. Any authenticated user can self-grant a 1-year Premium subscription without ever paying. Version 3.4.0 rejects sessions unless `session.payment_status === 'paid'` AND `session.status === 'complete'` (fails closed). Additionally, new unique `stripeCheckoutSessionId` column → a session can't be redeemed twice (race-safe via DB unique constraint).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47127.json
- https://github.com/ghostfolio/ghostfolio/security/advisories/GHSA-j465-x2w3-wjj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-47127
- https://github.com/ghostfolio/ghostfolio/pull/6872
