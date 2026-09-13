# [C] CVE-2025-63386

## Summary
Severity: Critical
Advisory: CVE-2025-63386
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-63386
Type: osv

## Details
A Cross-Origin Resource Sharing (CORS) misconfiguration vulnerability exists in Dify v1.9.1 in the /console/api/setup endpoint. The endpoint implements an insecure CORS policy that reflects any Origin header and enables Access-Control-Allow-Credentials: true, permitting arbitrary external domains to make authenticated requests. NOTE: the Supplier disputes this because the endpoint configuration is intentional to support bootstrap.

## References
- https://gist.github.com/Cristliu/1610daac87c711ac3e0250c58f5cc4f9
- https://gist.github.com/Cristliu/8ad993126be05c9210c71cc7d49fa112
- https://github.com/langgenius/dify/discussions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63386.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63386
- https://github.com/langgenius/dify/pull/32224
