# [M] Apache APISIX: improper validation of issuer from introspection discovery url in plugin openid-connect

## Summary
Severity: Medium
Advisory: BIT-apisix-2025-46647
Aliases: CVE-2025-46647
Ecosystem: Bitnami
Published: 2025-07-04
Source: https://osv.dev/vulnerability/BIT-apisix-2025-46647
Type: osv

## Affected
- Bitnami: `apisix` — affected >=0 <3.12.0

## Details
A vulnerability of plugin openid-connect in Apache APISIX.

This vulnerability will only have an impact if all of the following conditions are met:
1. Use the openid-connect plugin with introspection mode
2. The auth service connected to openid-connect provides services to multiple issuers
3. Multiple issuers share the same private key and relies only on the issuer being different

If affected by this vulnerability, it would allow an attacker with a valid account on one of the issuers to log into the other issuer.




This issue affects Apache APISIX: until 3.12.0.

Users are recommended to upgrade to version 3.12.0 or higher.

## References
- https://lists.apache.org/thread/yrpp2cd3o4qkxlrh421mq8gsrt0k4x0w
- https://nvd.nist.gov/vuln/detail/CVE-2025-46647
- http://www.openwall.com/lists/oss-security/2025/07/02/1
