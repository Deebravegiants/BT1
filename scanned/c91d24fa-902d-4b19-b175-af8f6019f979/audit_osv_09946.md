# [C] CVE-2017-12424

## Summary
Severity: Critical
Advisory: CVE-2017-12424
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12424
Type: osv

## Details
In shadow before 4.5, the newusers tool could be made to manipulate internal data structures in ways unintended by the authors. Malformed input may lead to crashes (with a buffer overflow or other memory corruption) or other unspecified behaviors. This crosses a privilege boundary in, for example, certain web-hosting environments in which a Control Panel allows an unprivileged user account to create subaccounts.

## References
- https://lists.debian.org/debian-lts-announce/2021/03/msg00020.html
- https://security.gentoo.org/glsa/201710-16
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=756630
- https://bugs.launchpad.net/ubuntu/+source/shadow/+bug/1266675
- https://github.com/shadow-maint/shadow/commit/954e3d2e7113e9ac06632aee3c69b8d818cc8952
