# [M] Kitty has an Arbitrary File Write via Symlink Race Condition in File Transmission Protocol

## Summary
Severity: Medium
Advisory: CVE-2026-54055
Aliases: GHSA-q446-x7q6-vcxh
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:L)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-54055
Type: osv

## Details
Kitty is a cross-platform GPU based terminal. In versions prior to 0.47.2, a local privilege escalation vulnerability exists in kitty's file transmission protocol where a child process running in the terminal can write to arbitrary files on the filesystem by exploiting a TOCTOU (Time-of-Check-Time-of-Use) race condition between symlink validation and file creation. The `os.open()` call used to create files does not use `O_NOFOLLOW`, allowing an attacker to create a symlink between the initial stat check and the actual file open, causing the write to follow the symlink to an arbitrary destination. Version 0.47.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54055.json
- https://github.com/kovidgoyal/kitty/security/advisories/GHSA-q446-x7q6-vcxh
- https://nvd.nist.gov/vuln/detail/CVE-2026-54055
