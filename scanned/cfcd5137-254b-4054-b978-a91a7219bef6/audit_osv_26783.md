# [C] Serendipity 2.4.0 Authenticated Remote Code Execution via File Upload

## Summary
Severity: Critical
Advisory: CVE-2023-53933
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2023-53933
Type: osv

## Details
Serendipity 2.4.0 contains a remote code execution vulnerability that allows authenticated attackers to upload malicious PHP files with .phar extension. Attackers can upload files with system command payloads to the media upload endpoint and execute arbitrary commands on the server.

## References
- https://docs.s9y.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53933.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53933
- https://www.vulncheck.com/advisories/serendipity-authenticated-remote-code-execution-via-file-upload
- https://www.exploit-db.com/exploits/51372
