# [C] CVE-2018-20179

## Summary
Severity: Critical
Advisory: CVE-2018-20179
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-15
Source: https://osv.dev/vulnerability/CVE-2018-20179
Type: osv

## Details
rdesktop versions up to and including v1.8.3 contain an Integer Underflow that leads to a Heap-Based Buffer Overflow in the function lspci_process() and results in memory corruption and probably even a remote code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00040.html
- http://www.securityfocus.com/bid/106938
- https://lists.debian.org/debian-lts-announce/2019/02/msg00030.html
- https://security.gentoo.org/glsa/201903-06
- https://www.debian.org/security/2019/dsa-4394
- https://github.com/rdesktop/rdesktop/commit/4dca546d04321a610c1835010b5dad85163b65e1
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
