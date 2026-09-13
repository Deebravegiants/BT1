# [H] CVE-2023-2110

## Summary
Severity: High
Advisory: CVE-2023-2110
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2023-08-19
Source: https://osv.dev/vulnerability/CVE-2023-2110
Type: osv

## Details
Improper path handling in Obsidian desktop before 1.2.8 on Windows, Linux and macOS allows a crafted webpage to access local files and exfiltrate them to remote web servers via "app://local/<absolute-path>". This vulnerability can be exploited if a user opens a malicious markdown file in Obsidian, or copies text from a malicious webpage and paste it into Obsidian.

## References
- https://obsidian.md/changelog/2023-05-03-desktop-v1.2.8/
- https://starlabs.sg/advisories/23/23-2110/
