# [H] CVE-2019-17177

## Summary
Severity: High
Advisory: CVE-2019-17177
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-04
Source: https://osv.dev/vulnerability/CVE-2019-17177
Type: osv

## Details
libfreerdp/codec/region.c in FreeRDP through 1.1.x and 2.x through 2.0.0-rc4 has memory leaks because a supplied realloc pointer (i.e., the first argument to realloc) is also used for a realloc return value.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00005.html
- https://github.com/FreeRDP/FreeRDP/issues/5645
- https://security.gentoo.org/glsa/202005-07
- https://usn.ubuntu.com/4379-1/
- https://github.com/FreeRDP/FreeRDP/commit/9fee4ae076b1ec97b97efb79ece08d1dab4df29a
