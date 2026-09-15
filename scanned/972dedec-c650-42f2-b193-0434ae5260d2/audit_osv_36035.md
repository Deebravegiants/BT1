# [M] Insufficient verification of lifetime-deal redemption codes allows forgery of permanent paid subscriptions

## Summary
Severity: Medium
Advisory: CVE-2026-19127
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-19127
Type: osv

## Details
An issue in the billing and license activation subsystem allows remote attackers to bypass payment authorization workflows. By exploiting insufficient cryptographic validation or lack of server-side state verification on promotional/lifetime-deal (LTD) redemption codes, an unauthenticated attacker can forge valid redemption tokens or replay existing single-use codes to activate permanent, tier-highest paid subscriptions without a financial transaction.

## References
- https://gadvisory.org/advisories/PSA-2026-NWZN9J
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19127.json
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.10
- https://nvd.nist.gov/vuln/detail/CVE-2026-19127
- https://github.com/gitroomhq/postiz-app/commit/387d85dabe0223cd930714c19072a0aee58541ca
