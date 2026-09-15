# [M] CVE-2024-46257

## Summary
Severity: Medium
Advisory: CVE-2024-46257
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46257
Type: osv

## Details
A Command injection vulnerability in requestLetsEncryptSslWithDnsChallenge in NginxProxyManager 2.11.3 allows an attacker to achieve remote code execution via Add Let's Encrypt Certificate. NOTE: this is not part of any NGINX software shipped by F5.

## References
- https://github.com/NginxProxyManager/nginx-proxy-manager/blob/v2.11.3/backend/internal/certificate.js#L870
- https://github.com/NginxProxyManager/nginx-proxy-manager/pull/4073/commits/c39d5433bcd13993def222bbb2b6988bbb810a05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46257.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46257
- https://github.com/NginxProxyManager/nginx-proxy-manager/commit/99cce7e2b0da2978411cedd7cac5fffbe15bc466
- https://github.com/barttran2k/POC_CVE-2024-46256
