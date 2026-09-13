# [C] CVE-2021-35942

## Summary
Severity: Critical
Advisory: CVE-2021-35942
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-07-22
Source: https://osv.dev/vulnerability/CVE-2021-35942
Type: osv

## Details
The wordexp function in the GNU C Library (aka glibc) through 2.33 may crash or read arbitrary memory in parse_param (in posix/wordexp.c) when called with an untrusted, crafted pattern, potentially resulting in a denial of service or disclosure of information. This occurs because atoi was used but strtoul should have been used to ensure correct calculations.

## References
- https://sourceware.org/git/?p=glibc.git%3Ba=commit%3Bh=5adda61f62b77384718b4c0d8336ade8f2b4b35c
- https://sourceware.org/glibc/wiki/Security%20Exceptions
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html
- https://security.gentoo.org/glsa/202208-24
- https://security.netapp.com/advisory/ntap-20210827-0005/
- https://sourceware.org/bugzilla/show_bug.cgi?id=28011
