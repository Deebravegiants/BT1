# [C] Nginx Proxy Manager Authenticated RCE via setupCertbotPlugins()

## Summary
Severity: Critical
Advisory: CVE-2026-40519
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-40519
Type: osv

## Details
Nginx Proxy Manager versions 2.9.14 through 2.15.1, fixed in commit a5db5ed, contain an authenticated remote code execution vulnerability via OS command injection in the setupCertbotPlugins() function in backend/setup.js, allowing attackers with certificates:manage permission to execute arbitrary commands by storing a malicious payload in the dns_provider_credentials field. The user-controlled dns_provider_credentials value is interpolated directly into a shell command executed via child_process.exec() without sanitization or escaping, causing the injected command to execute upon backend restart.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40519.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40519
- https://www.vulncheck.com/advisories/nginx-proxy-manager-authenticated-rce-via-setupcertbotplugins
- https://github.com/NginxProxyManager/nginx-proxy-manager/pull/5498
- https://github.com/NginxProxyManager/nginx-proxy-manager/commit/a5db5ed156355e3088e7d1ceb0533d4bae922def
- https://github.com/NginxProxyManager/nginx-proxy-manager
