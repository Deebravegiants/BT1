# [M] SSRF Vulnerability in gradio-app/gradio

## Summary
Severity: Medium
Advisory: CVE-2024-1183
Aliases: GHSA-qh6x-j82h-vpf9, PYSEC-2026-1419
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-1183
Type: osv

## Details
An SSRF (Server-Side Request Forgery) vulnerability exists in the gradio-app/gradio repository, allowing attackers to scan and identify open ports within an internal network. By manipulating the 'file' parameter in a GET request, an attacker can discern the status of internal ports based on the presence of a 'Location' header or a 'File not allowed' error in the response.

## References
- https://huntr.com/bounties/103434f9-87d2-42ea-9907-194a3c25007c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1183.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1183
- https://github.com/gradio-app/gradio/commit/2ad3d9e7ec6c8eeea59774265b44f11df7394bb4
