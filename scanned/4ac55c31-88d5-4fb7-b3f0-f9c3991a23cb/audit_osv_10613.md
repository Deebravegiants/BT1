# [M] CVE-2017-17788

## Summary
Severity: Medium
Advisory: CVE-2017-17788
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-17788
Type: osv

## Details
In GIMP 2.8.22, there is a stack-based buffer over-read in xcf_load_stream in app/xcf/xcf.c when there is no '\0' character after the version string.

## References
- http://www.openwall.com/lists/oss-security/2017/12/19/5
- https://lists.debian.org/debian-lts-announce/2017/12/msg00023.html
- https://usn.ubuntu.com/3539-1/
- https://www.debian.org/security/2017/dsa-4077
- https://bugzilla.gnome.org/show_bug.cgi?id=790783
