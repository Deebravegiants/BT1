# [H] Zulip Vulnerable to Modification of Payment Method (Stripe Default Card) by Non-Billing Users

## Summary
Severity: High
Advisory: CVE-2026-25741
Aliases: GHSA-vhhx-84f7-rc8j
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-25741
Type: osv

## Details
Zulip is an open-source team collaboration tool. Prior to commit bf28c82dc9b1f630fa8e9106358771b20a0040f7, the API endpoint for creating a card update session during an upgrade flow was accessible to users with only organization member privileges. When the associated Stripe Checkout session is completed, the Stripe webhook updates the organization’s default payment method. Because no billing-specific authorization check is enforced, a regular (non-billing) member can change the organization’s payment method. This vulnerability affected the Zulip Cloud payment processing system, and has been patched as of commit bf28c82dc9b1f630fa8e9106358771b20a0040f7. Self-hosted deploys are no longer affected and no patch or upgrade is required for them.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25741.json
- https://github.com/zulip/zulip/security/advisories/GHSA-vhhx-84f7-rc8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-25741
- https://github.com/zulip/zulip/commit/bf28c82dc9b1f630fa8e9106358771b20a0040f7
