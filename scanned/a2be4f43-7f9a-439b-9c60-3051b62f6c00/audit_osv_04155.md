# [H] Apache APISIX: Cas-auth Host header influence on CAS service URL

## Summary
Severity: High
Advisory: BIT-apisix-2026-48895
Aliases: CVE-2026-48895
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-48895
Type: osv

## Affected
- Bitnami: `apisix` — affected >=3.0.0 <3.17.0

## Details
URL Redirection to Untrusted Site ('Open Redirect') vulnerability in Apache APISIX.

The attacker could manipulate some client headers to perform an open-redirect, to potentially expose the session token.

This issue affects Apache APISIX: from 3.0.0 through 3.16.0.

Users are recommended to upgrade to version 3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/11
- https://lists.apache.org/thread/yo1kq93ds69zbgjjopop7dmzm7zhj1gq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48895
