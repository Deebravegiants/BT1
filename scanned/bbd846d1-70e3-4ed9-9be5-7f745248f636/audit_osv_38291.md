# [C] CVE-2026-37236

## Summary
Severity: Critical
Advisory: CVE-2026-37236
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-37236
Type: osv

## Details
grpc-gateway v2.28.0 is vulnerable to Incorrect Access Control. The application processes the X-HTTP-Method-Override header in ServeMux.ServeHTTP without restricting allowed methods. When a POST request with Content-Type application/x-www-form-urlencoded includes this header, the request method is rewritten to an arbitrary attacker-supplied value before routing. This allows bypassing method-based access controls enforced by upstream proxies or WAFs.

## References
- https://s00me00ne.com/cve/cve-2026-37236/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37236.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-37236
- https://github.com/grpc-ecosystem/grpc-gateway/commit/72123cd4f32545f6e1376873f412dcdcbcf29acc
- https://github.com/grpc-ecosystem/grpc-gateway
