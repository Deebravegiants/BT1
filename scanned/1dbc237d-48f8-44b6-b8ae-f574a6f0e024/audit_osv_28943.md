# [C] CVE-2024-38395

## Summary
Severity: Critical
Advisory: CVE-2024-38395
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-16
Source: https://osv.dev/vulnerability/CVE-2024-38395
Type: osv

## Details
In iTerm2 before 3.5.2, the "Terminal may report window title" setting is not honored, and thus remote code execution might occur but "is not trivially exploitable."

## References
- https://gitlab.com/gnachman/iterm2/-/tags/v3.5.2
- https://iterm2.com/downloads.html
- https://www.openwall.com/lists/oss-security/2024/06/15/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38395.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38395
- https://gitlab.com/gnachman/iterm2/-/commit/f1e89f78dd72dcac3ba66d3d6f93db3f7f649219
- http://www.openwall.com/lists/oss-security/2024/06/17/1
