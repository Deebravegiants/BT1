# [H] CVE-2023-35843

## Summary
Severity: High
Advisory: CVE-2023-35843
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-19
Source: https://osv.dev/vulnerability/CVE-2023-35843
Type: osv

## Details
NocoDB through 0.106.0 (or 0.109.1) has a path traversal vulnerability that allows an unauthenticated attacker to access arbitrary files on the server by manipulating the path parameter of the /download route. This vulnerability could allow an attacker to access sensitive files and data on the server, including configuration files, source code, and other sensitive information.

## References
- https://github.com/nocodb/nocodb/blob/6decfa2b20c28db9946bddce0bcb1442b683ecae/packages/nocodb/src/lib/controllers/attachment.ctl.ts#L62-L74
- https://github.com/nocodb/nocodb/blob/f7ee7e3beb91d313a159895d1edc1aba9d91b0bc/packages/nocodb/src/controllers/attachments.controller.ts#L55-L66
- https://advisory.dw1.io/60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35843.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-35843
