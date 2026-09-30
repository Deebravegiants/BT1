# [H] Vvveb: checkout IDOR allows unauthorized reuse of another user's cart

## Summary
Severity: High
Advisory: CVE-2026-46408
Aliases: GHSA-rmh2-wv73-xpqh
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-46408
Type: osv

## Details
Vvveb is a powerful and easy to use CMS with page builder to build websites, blogs or ecommerce stores. Prior to 1.0.8.3, the checkout endpoint accepts a user-controlled cart_id and uses it to enter the payment flow without verifying cart ownership. A logged-in attacker can therefore reuse another user's cart data in their own checkout session. This vulnerability is fixed in 1.0.8.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46408.json
- https://github.com/givanz/Vvveb/security/advisories/GHSA-rmh2-wv73-xpqh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46408
