# [M] CVE-2025-50579

## Summary
Severity: Medium
Advisory: CVE-2025-50579
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-50579
Type: osv

## Details
A CORS misconfiguration in Nginx Proxy Manager v2.12.3 allows unauthorized domains to access sensitive data, particularly JWT tokens, due to improper validation of the Origin header. This misconfiguration enables attackers to intercept tokens using a simple browser script and exfiltrate them to a remote attacker-controlled server, potentially leading to unauthorized actions within the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50579.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50579
- https://github.com/NginxProxyManager/nginx-proxy-manager/issues/4509
- https://github.com/NginxProxyManager/nginx-proxy-manager
