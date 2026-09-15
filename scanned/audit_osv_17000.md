# [H] CVE-2020-11073

## Summary
Severity: High
Advisory: CVE-2020-11073
Aliases: GHSA-h8wm-cqq6-957q
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-13
Source: https://osv.dev/vulnerability/CVE-2020-11073
Type: osv

## Details
In Autoswitch Python Virtualenv before version 0.16.0, a user who enters a directory with a malicious `.venv` file could run arbitrary code without any user interaction. This is fixed in version: 1.16.0

## References
- https://github.com/MichaelAquilina/zsh-autoswitch-virtualenv/pull/123
- https://github.com/MichaelAquilina/zsh-autoswitch-virtualenv/security/advisories/GHSA-h8wm-cqq6-957q
- https://github.com/MichaelAquilina/zsh-autoswitch-virtualenv/commit/30c77db7c83eca2bc5f6134fccbdc117b49a6a05
- https://github.com/MichaelAquilina/zsh-autoswitch-virtualenv/issues/122
