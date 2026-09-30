# [H] CVE-2023-23596

## Summary
Severity: High
Advisory: CVE-2023-23596
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-20
Source: https://osv.dev/vulnerability/CVE-2023-23596
Type: osv

## Details
jc21 NGINX Proxy Manager through 2.9.19 allows OS command injection. When creating an access list, the backend builds an htpasswd file with crafted username and/or password input that is concatenated without any validation, and is directly passed to the exec command, potentially allowing an authenticated attacker to execute arbitrary commands on the system. NOTE: this is not part of any NGINX software shipped by F5.

## References
- https://github.com/NginxProxyManager/nginx-proxy-manager/blob/4f10d129c20cc82494b95cc94b97f859dbd4b54d/backend/internal/access-list.js#L510
- https://advisory.dw1.io/57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23596.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23596
