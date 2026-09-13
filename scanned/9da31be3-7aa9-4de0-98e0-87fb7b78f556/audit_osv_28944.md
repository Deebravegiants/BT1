# [C] CVE-2024-38396

## Summary
Severity: Critical
Advisory: CVE-2024-38396
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-16
Source: https://osv.dev/vulnerability/CVE-2024-38396
Type: osv

## Details
An issue was discovered in iTerm2 3.5.x before 3.5.2. Unfiltered use of an escape sequence to report a window title, in combination with the built-in tmux integration feature (enabled by default), allows an attacker to inject arbitrary code into the terminal, a different vulnerability than CVE-2024-38395.

## References
- https://iterm2.com/downloads.html
- https://vin01.github.io/piptagole/escape-sequences/iterm2/rce/2024/06/16/iterm2-rce-window-title-tmux-integration.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38396.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38396
- https://gitlab.com/gnachman/iterm2/-/commit/fc60236a914d63fb70a5c632e211203a4f1bd4dd
- http://www.openwall.com/lists/oss-security/2024/06/17/1
