# [C] CVE-2025-63388

## Summary
Severity: Critical
Advisory: CVE-2025-63388
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-63388
Type: osv

## Details
A Cross-Origin Resource Sharing (CORS) misconfiguration vulnerability exists in Dify v1.9.1 in the /console/api/system-features endpoint. The endpoint implements an overly permissive CORS policy that reflects arbitrary Origin headers and sets Access-Control-Allow-Credentials: true, allowing any external domain to make authenticated cross-origin requests. NOTE: the Supplier disputes this, providing the rationale of "sending requests with credentials does not provide any additional access compared to unauthenticated requests."

## References
- https://gist.github.com/Cristliu/5ded6d03e41d7d66ecb1b568bae3ff6c
- https://gist.github.com/Cristliu/c2bc7d05abd89db8eb542a453a528d77
- https://github.com/langgenius/dify/discussions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63388.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63388
