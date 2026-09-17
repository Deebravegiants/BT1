# [H] CVE-2021-20212

## Summary
Severity: High
Advisory: CVE-2021-20212
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/CVE-2021-20212
Type: osv

## Details
A flaw was found in Privoxy in versions before 3.0.29. Memory leak if multiple filters are executed and the last one is skipped due to a pcre error leading to a system crash.

## References
- https://security.gentoo.org/glsa/202107-16
- https://www.privoxy.org/3.0.29/user-manual/whatsnew.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1928736
