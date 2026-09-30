# [H] CVE-2019-12106

## Summary
Severity: High
Advisory: CVE-2019-12106
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-15
Source: https://osv.dev/vulnerability/CVE-2019-12106
Type: osv

## Details
The updateDevice function in minissdpd.c in MiniUPnP MiniSSDPd 1.4 and 1.5 allows a remote attacker to crash the process due to a Use After Free vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00037.html
- https://github.com/miniupnp/miniupnp/commit/cd506a67e174a45c6a202eff182a712955ed6d6f
- https://www.vdoo.com/blog/security-issues-discovered-in-miniupnp
