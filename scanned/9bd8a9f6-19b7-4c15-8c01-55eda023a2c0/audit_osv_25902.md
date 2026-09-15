# [M] CVE-2023-46988

## Summary
Severity: Medium
Advisory: CVE-2023-46988
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2023-46988
Type: osv

## Details
Path Traversal vulnerability in ONLYOFFICE Document Server before v8.0.1 allows a remote attacker to copy arbitrary files by manipulating the fileExt parameter in the /example/editor endpoint, leading to unauthorized access to sensitive files and potential Denial of Service (DoS).

## References
- https://medium.com/@mihat2/onlyoffice-document-server-path-traversal-fdd573fec291
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46988.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-46988
