# [H] apisix/jwt-auth may leak secrets in error response

## Summary
Severity: High
Advisory: BIT-apisix-2022-29266
Aliases: CVE-2022-29266
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apisix-2022-29266
Type: osv

## Affected
- Bitnami: `apisix` — affected >=0 <2.13.1

## Details
In APache APISIX before 3.13.1, the jwt-auth plugin has a security issue that leaks the user's secret key because the error message returned from the dependency lua-resty-jwt contains sensitive information.

## References
- http://www.openwall.com/lists/oss-security/2022/04/20/1
- https://lists.apache.org/thread/6qpfyxogbvn18g9xr8g218jjfjbfsbhr
- https://nvd.nist.gov/vuln/detail/CVE-2022-29266
