# [H] CVE-2021-20213

## Summary
Severity: High
Advisory: CVE-2021-20213
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/CVE-2021-20213
Type: osv

## Details
A flaw was found in Privoxy in versions before 3.0.29. Dereference of a NULL-pointer that could result in a crash if accept-intercepted-requests was enabled, Privoxy failed to get the request destination from the Host header and a memory allocation failed.

## References
- https://security.gentoo.org/glsa/202107-16
- https://www.privoxy.org/3.0.29/user-manual/whatsnew.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1928739
