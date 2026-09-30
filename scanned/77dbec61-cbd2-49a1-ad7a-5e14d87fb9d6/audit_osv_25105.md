# [H] ESPv2 vulnerable to JWT authentication bypass via `X-HTTP-Method-Override` header

## Summary
Severity: High
Advisory: CVE-2023-30845
Aliases: GHSA-6qmp-9p95-fc5f
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-04-26
Source: https://osv.dev/vulnerability/CVE-2023-30845
Type: osv

## Details
ESPv2 is a service proxy that provides API management capabilities using Google Service Infrastructure. ESPv2 2.20.0 through 2.42.0 contains an authentication bypass vulnerability. API clients can craft a malicious `X-HTTP-Method-Override` header value to bypass JWT authentication in specific cases.

ESPv2 allows malicious requests to bypass authentication if both the conditions are true: The requested HTTP method is **not** in the API service definition (OpenAPI spec or gRPC `google.api.http` proto annotations, and the specified `X-HTTP-Method-Override` is a valid HTTP method in the API service definition. ESPv2 will forward the request to your backend without checking the JWT. Attackers can craft requests with a malicious `X-HTTP-Method-Override` value that allows them to bypass specifying JWTs. Restricting API access with API keys works as intended and is not affected by this vulnerability.

Upgrade deployments to release v2.43.0 or higher to receive a patch. This release ensures that JWT authentication occurs, even when the caller specifies `x-http-method-override`. `x-http-method-override` is still supported by v2.43.0+. API clients can continue sending this header to ESPv2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30845.json
- https://github.com/GoogleCloudPlatform/esp-v2/security/advisories/GHSA-6qmp-9p95-fc5f
- https://nvd.nist.gov/vuln/detail/CVE-2023-30845
- https://github.com/GoogleCloudPlatform/esp-v2/commit/0bcdfc024ce96b34db4e1b4f2211b509d9be93cd
- https://github.com/GoogleCloudPlatform/esp-v2/commit/e95670146f5e96bb5565b0a9c1e153886b3e04ce
- https://github.com/GoogleCloudPlatform/esp-v2/commit/e98061ee4527a564506ba4e814c0ecf324dc2c6f
