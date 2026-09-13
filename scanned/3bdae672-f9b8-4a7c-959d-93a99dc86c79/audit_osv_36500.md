# [H] CVE-2026-23920

## Summary
Severity: High
Advisory: CVE-2026-23920
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-23920
Type: osv

## Details
Host and event action script input is validated with a regex (set by the administrator), but the validation runs in multiline mode. If ^ and $ anchors are used in user input validation, an injected newline lets authenticated users bypass the check and inject shell commands.

## References
- https://support.zabbix.com/browse/ZBX-27639
