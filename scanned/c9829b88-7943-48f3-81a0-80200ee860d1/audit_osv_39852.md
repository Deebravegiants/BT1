# [H] Spring Cloud Gateway SSRF and native file access with gRPC

## Summary
Severity: High
Advisory: CVE-2026-47879
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-47879
Type: osv

## Details
Spring Cloud Gateway JsonToGrpcGatewayFilterFactory allows arbitrary Spring Resource locations for defining the proto descriptor.
Spring Cloud Gateway 5.0.0 - 5.0.2
Spring Cloud Gateway 4.3.0 - 4.3.5
Spring Cloud Gateway 4.0.0 - 4.2.9
Spring Cloud Gateway 3.1.13 and earlier

## References
- https://spring.io/security/cve-2026-47879
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47879.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47879
