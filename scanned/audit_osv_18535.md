# [H] CVE-2020-28407

## Summary
Severity: High
Advisory: CVE-2020-28407
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2020-28407
Type: osv

## Details
In swtpm before 0.4.2 and 0.5.x before 0.5.1, a local attacker may be able to overwrite arbitrary files via a symlink attack against a temporary file such as TMP2-00.permall.

## References
- https://github.com/stefanberger/swtpm/releases/tag/v0.4.2
- https://github.com/stefanberger/swtpm/releases/tag/v0.5.1
- https://bugzilla.suse.com/show_bug.cgi?id=1198395
