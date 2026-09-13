# [M] CVE-2024-55452

## Summary
Severity: Medium
Advisory: CVE-2024-55452
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-12-16
Source: https://osv.dev/vulnerability/CVE-2024-55452
Type: osv

## Details
A URL redirection vulnerability exists in UJCMS 9.6.3 due to improper validation of URLs in the upload and rendering of new block / carousel items. This vulnerability allows authenticated attackers to redirect unprivileged users to an arbitrary, attacker-controlled webpage. When an authenticated user clicks on the malicious block item, they are redirected to the arbitrary untrusted domains, where sensitive tokens, such as JSON Web Tokens, can be stolen via a crafted webpage.

## References
- https://github.com/cydtseng/Vulnerability-Research/blob/main/ujcms/OpenRedirect-BlockItemUpload.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55452.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55452
- https://github.com/dromara/ujcms
