# [H] JLSEC-2026-528

## Summary
Severity: High
Advisory: JLSEC-2026-528
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-528
Type: osv

## Affected
- Julia: `tmux_jll` — affected >=0 <3.3.0+0

## Details
In tmux before version 3.1c the function `input_csi_dispatch_sgr_colon()` in file input.c contained a stack-based buffer-overflow that can be exploited by terminal output.

## References
- https://github.com/tmux/tmux/commit/a868bacb46e3c900530bed47a1c6f85b0fbe701c
- https://raw.githubusercontent.com/tmux/tmux/3.1c/CHANGES
- https://security.gentoo.org/glsa/202011-10
- https://www.openwall.com/lists/oss-security/2020/11/05/3
