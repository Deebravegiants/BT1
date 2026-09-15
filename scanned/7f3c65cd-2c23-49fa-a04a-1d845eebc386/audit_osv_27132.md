# [H] Local File Read (LFI) by Tarslip Symlink via arxiv_download() API in binary-husky/gpt_academic

## Summary
Severity: High
Advisory: CVE-2024-10986
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10986
Type: osv

## Details
GPT Academic version 3.83 is vulnerable to a Local File Read (LFI) vulnerability through its HotReload function. This function can download and extract tar.gz files from arxiv.org. Despite implementing protections against path traversal, the application overlooks the Tarslip triggered by symlinks. This oversight allows attackers to read arbitrary local files from the victim server.

## References
- https://huntr.com/bounties/db2167f5-f17f-491d-aeec-69ba55bf6427
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10986.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10986
