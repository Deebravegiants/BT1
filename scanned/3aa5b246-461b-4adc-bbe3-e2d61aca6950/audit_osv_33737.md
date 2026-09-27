# [H] CVE-2025-49619

## Summary
Severity: High
Advisory: CVE-2025-49619
Aliases: GHSA-h92g-3xc3-ww2r, PYSEC-2026-1929
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2025-06-07
Source: https://osv.dev/vulnerability/CVE-2025-49619
Type: osv

## Details
Skyvern through 0.1.85 is vulnerable to server-side template injection (SSTI) in the Prompt field of workflow blocks such as the Navigation v2 Block. Improper sanitization of Jinja2 template input allows authenticated users to inject crafted expressions that are evaluated on the server, leading to blind remote code execution (RCE).

## References
- https://cristibtz.github.io/posts/CVE-2025-49619/
- https://www.exploit-db.com/exploits/52335
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49619.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49619
- https://github.com/Skyvern-AI/skyvern/commit/db856cd8433a204c8b45979c70a4da1e119d949d
- https://cristibtz.blog/posts/CVE-2025-49619/
