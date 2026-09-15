# [H] CVE-2019-12107

## Summary
Severity: High
Advisory: CVE-2019-12107
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-05-15
Source: https://osv.dev/vulnerability/CVE-2019-12107
Type: osv

## Details
The upnp_event_prepare function in upnpevents.c in MiniUPnP MiniUPnPd through 2.1 allows a remote attacker to leak information from the heap due to improper validation of an snprintf return value.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00045.html
- https://usn.ubuntu.com/4542-1/
- https://github.com/miniupnp/miniupnp/commit/bec6ccec63cadc95655721bc0e1dd49dac759d94
- https://www.vdoo.com/blog/security-issues-discovered-in-miniupnp
