# [C] CVE-2018-8793

## Summary
Severity: Critical
Advisory: CVE-2018-8793
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/CVE-2018-8793
Type: osv

## Details
rdesktop versions up to and including v1.8.3 contain a Heap-Based Buffer Overflow in function cssp_read_tsrequest() that results in a memory corruption and probably even a remote code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00040.html
- http://www.securityfocus.com/bid/106938
- https://lists.debian.org/debian-lts-announce/2019/02/msg00030.html
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
- https://security.gentoo.org/glsa/201903-06
- https://www.debian.org/security/2019/dsa-4394
- https://github.com/rdesktop/rdesktop/commit/4dca546d04321a610c1835010b5dad85163b65e1
