# [H] CVE-2017-15108

## Summary
Severity: High
Advisory: CVE-2017-15108
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-20
Source: https://osv.dev/vulnerability/CVE-2017-15108
Type: osv

## Details
spice-vdagent up to and including 0.17.0 does not properly escape save directory before passing to shell, allowing local attacker with access to the session the agent runs in to inject arbitrary commands to be executed.

## References
- https://lists.debian.org/debian-lts-announce/2021/01/msg00012.html
- https://security.gentoo.org/glsa/201804-09
- https://cgit.freedesktop.org/spice/linux/vd_agent/commit/?id=8ba174816d245757e743e636df357910e1d5eb61
