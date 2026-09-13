# [H] CVE-2018-20174

## Summary
Severity: High
Advisory: CVE-2018-20174
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-15
Source: https://osv.dev/vulnerability/CVE-2018-20174
Type: osv

## Details
rdesktop versions up to and including v1.8.3 contain an Out-Of-Bounds Read in the function ui_clip_handle_data() that results in an information leak.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00040.html
- http://www.securityfocus.com/bid/106938
- https://lists.debian.org/debian-lts-announce/2019/02/msg00030.html
- https://security.gentoo.org/glsa/201903-06
- https://www.debian.org/security/2019/dsa-4394
- https://github.com/rdesktop/rdesktop/commit/4dca546d04321a610c1835010b5dad85163b65e1
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
