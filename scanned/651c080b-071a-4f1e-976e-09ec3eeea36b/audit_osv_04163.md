# [H] Apache APISIX: ldap-auth plugin cross-subtree identity impersonation

## Summary
Severity: High
Advisory: BIT-apisix-2026-75020
Aliases: CVE-2026-75020
Ecosystem: Bitnami
Published: 2026-09-01
Source: https://osv.dev/vulnerability/BIT-apisix-2026-75020
Type: osv

## Affected
- Bitnami: `apisix` — affected >=2.11.0 <3.18.0

## Details
Improper Neutralization of Special Elements used in an LDAP Query ('LDAP Injection') vulnerability in Apache APISIX.

A caller who holds valid credentials for one entry in the LDAP directory can authenticate through APISIX as a consumer mapped to a different entry, one the plugin's configured scope was meant to keep out of reach.


This issue affects Apache APISIX: from 2.11.0 through 3.17.0.



Users are recommended to upgrade to version 3.18.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/14
- https://lists.apache.org/thread/d4007wk6dbl9mxy5h05zxwn8fsg13bxt
- https://nvd.nist.gov/vuln/detail/CVE-2026-75020
