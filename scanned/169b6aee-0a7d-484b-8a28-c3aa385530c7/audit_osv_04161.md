# [H] Apache APISIX: Cross-user response poisoning in serverless plugins

## Summary
Severity: High
Advisory: BIT-apisix-2026-74848
Aliases: CVE-2026-74848
Ecosystem: Bitnami
Published: 2026-09-01
Source: https://osv.dev/vulnerability/BIT-apisix-2026-74848
Type: osv

## Affected
- Bitnami: `apisix` — affected >=2.12.0 <3.18.0

## Details
Inconsistent Interpretation of HTTP Requests ('HTTP Request/Response Smuggling') vulnerability in Apache APISIX.

An attacker could make other clients receive attacker-chosen or other users' responses on serverless-plugin routes.




This issue affects Apache APISIX: from 2.12.0 through 3.17.0.



Users are recommended to upgrade to version 3.18.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/12
- https://lists.apache.org/thread/xdgpszmw8dw4wvmfxy043d83m150kx3n
- https://nvd.nist.gov/vuln/detail/CVE-2026-74848
