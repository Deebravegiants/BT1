# [H] Server-Side Request Forgery (SSRF) in gaizhenbiao/ChuanhuChatGPT

## Summary
Severity: High
Advisory: CVE-2024-5822
Aliases: PYSEC-2024-268
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-5822
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the upload processing interface of gaizhenbiao/ChuanhuChatGPT versions <= ChuanhuChatGPT-20240410-git.zip. This vulnerability allows attackers to send crafted requests from the vulnerable server to internal or external resources, potentially bypassing security controls and accessing sensitive data.

## References
- https://huntr.com/bounties/b24f1b5f-a529-435b-ac4d-5ca71d5d1fb5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5822.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5822
