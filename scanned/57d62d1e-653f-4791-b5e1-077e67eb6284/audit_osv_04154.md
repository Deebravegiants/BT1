# [M] Apache APISIX: Session replay issue in hmac-auth

## Summary
Severity: Medium
Advisory: BIT-apisix-2026-47341
Aliases: CVE-2026-47341
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-47341
Type: osv

## Affected
- Bitnami: `apisix` — affected >=3.11.0 <3.18.0

## Details
Authentication Bypass by Capture-replay vulnerability in Apache APISIX.

Attacker can benefit from certain configurations in hmac-auth to re-use a token forever, bypassing expiry.
This issue affects Apache APISIX: from 3.11.0 through 3.16.0.

Users are recommended to upgrade to version 3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/10
- https://lists.apache.org/thread/ob6ng9x2hxtyfojs839hs1n0v18xxzf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-47341
