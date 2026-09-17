# [H] Postiz: Unauthenticated arbitrary lifetime PRO grant via Nowpayments webhook

## Summary
Severity: High
Advisory: CVE-2026-48799
Aliases: GHSA-j7rp-5mgj-qgg9
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-48799
Type: osv

## Details
Postiz is an AI social media scheduling tool. Prior to 2.21.8, Postiz fails to verify Nowpayments IPN callback authenticity against the payment provider shared secret and reads the target subscription identifier from the untrusted request body, allowing a low-privileged account to grant arbitrary organizations lifetime PRO subscriptions without payment. This issue is fixed in version 2.21.8.

## References
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.8
- https://gadvisory.org/advisories/PSA-2026-Q3TCPK
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48799.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-j7rp-5mgj-qgg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48799
- https://github.com/gitroomhq/postiz-app/commit/23696d2973510ae1f3f48bfa41a6bfbbf9827b05
