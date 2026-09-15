# [C] CVE-2023-34409

## Summary
Severity: Critical
Advisory: CVE-2023-34409
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-06
Source: https://osv.dev/vulnerability/CVE-2023-34409
Type: osv

## Details
In Percona Monitoring and Management (PMM) server 2.x before 2.37.1, the authenticate function in auth_server.go does not properly formalize and sanitize URL paths to reject path traversal attempts. This allows an unauthenticated remote user, when a crafted POST request is made against unauthenticated API routes, to access otherwise protected API routes leading to escalation of privileges and information disclosure.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34409.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34409
- https://www.percona.com/blog/pmm-authentication-bypass-vulnerability-fixed-in-2-37-1/
