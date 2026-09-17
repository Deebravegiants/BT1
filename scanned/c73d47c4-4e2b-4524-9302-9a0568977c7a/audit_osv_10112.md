# [M] CVE-2017-13734

## Summary
Severity: Medium
Advisory: CVE-2017-13734
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13734
Type: osv

## Details
There is an illegal address access in the _nc_safe_strcat function in strings.c in ncurses 6.0 that will lead to a remote denial of service attack.

## References
- https://security.gentoo.org/glsa/201804-13
- https://bugzilla.redhat.com/show_bug.cgi?id=1484291
