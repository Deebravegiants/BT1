# [H] CVE-2024-39935

## Summary
Severity: High
Advisory: CVE-2024-39935
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-04
Source: https://osv.dev/vulnerability/CVE-2024-39935
Type: osv

## Details
jc21 NGINX Proxy Manager before 2.11.3 allows backend/internal/certificate.js OS command injection by an authenticated user (with certificate management privileges) via untrusted input to the DNS provider configuration. NOTE: this is not part of any NGINX software shipped by F5.

## References
- https://github.com/NginxProxyManager/nginx-proxy-manager/compare/v2.11.2...v2.11.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39935.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39935
- https://github.com/NginxProxyManager/nginx-proxy-manager/issues/3662
- https://github.com/NginxProxyManager/nginx-proxy-manager/commit/99cce7e2b0da2978411cedd7cac5fffbe15bc46
