# [C] CVE-2017-10685

## Summary
Severity: Critical
Advisory: CVE-2017-10685
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-29
Source: https://osv.dev/vulnerability/CVE-2017-10685
Type: osv

## Details
In ncurses 6.0, there is a format string vulnerability in the fmt_entry function. A crafted input will lead to a remote arbitrary code execution attack.

## References
- https://security.gentoo.org/glsa/201804-13
- https://bugzilla.redhat.com/show_bug.cgi?id=1464692
