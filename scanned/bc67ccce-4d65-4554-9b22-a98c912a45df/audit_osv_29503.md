# [H] Local File Inclusion (LFI) in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: High
Advisory: CVE-2024-4321
Aliases: PYSEC-2024-267
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/CVE-2024-4321
Type: osv

## Details
A Local File Inclusion (LFI) vulnerability exists in the gaizhenbiao/chuanhuchatgpt application, specifically within the functionality for uploading chat history. The vulnerability arises due to improper input validation when handling file paths during the chat history upload process. An attacker can exploit this vulnerability by intercepting requests and manipulating the 'name' parameter to specify arbitrary file paths. This allows the attacker to read sensitive files on the server, leading to information leakage, including API keys and private information. The issue affects version 20240310 of the application.

## References
- https://huntr.com/bounties/19a16f8e-3d92-498f-abc9-8686005f067e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4321.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4321
