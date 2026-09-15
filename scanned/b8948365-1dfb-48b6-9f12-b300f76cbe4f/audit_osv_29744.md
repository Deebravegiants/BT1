# [C] CVE-2024-46256

## Summary
Severity: Critical
Advisory: CVE-2024-46256
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46256
Type: osv

## Details
A Command injection vulnerability in requestLetsEncryptSsl in NginxProxyManager 2.11.3 allows an attacker to RCE via Add Let's Encrypt Certificate.

## References
- https://github.com/NginxProxyManager/nginx-proxy-manager/blob/v2.11.3/backend/internal/certificate.js#L830
- https://github.com/NginxProxyManager/nginx-proxy-manager/pull/4073/commits/c39d5433bcd13993def222bbb2b6988bbb810a05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46256.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46256
- https://github.com/NginxProxyManager/nginx-proxy-manager/commit/99cce7e2b0da2978411cedd7cac5fffbe15bc466
- https://github.com/barttran2k/POC_CVE-2024-46256
