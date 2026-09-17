# [H] Server-Side Request Forgery (SSRF) in gradio-app/gradio

## Summary
Severity: High
Advisory: CVE-2024-4325
Aliases: GHSA-973g-55hp-3frw, PYSEC-2026-1413
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-4325
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the gradio-app/gradio version 4.21.0, specifically within the `/queue/join` endpoint and the `save_url_to_cache` function. The vulnerability arises when the `path` value, obtained from the user and expected to be a URL, is used to make an HTTP request without sufficient validation checks. This flaw allows an attacker to send crafted requests that could lead to unauthorized access to the local network or the AWS metadata endpoint, thereby compromising the security of internal servers.

## References
- https://huntr.com/bounties/b34f084b-7d14-4f00-bc10-048a3a5aaf88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4325.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4325
