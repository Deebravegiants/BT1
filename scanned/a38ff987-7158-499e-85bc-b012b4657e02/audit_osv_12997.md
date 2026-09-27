# [C] CVE-2018-16840

## Summary
Severity: Critical
Advisory: CVE-2018-16840
Aliases: CURL-CVE-2018-16840
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2018-16840
Type: osv

## Details
A heap use-after-free flaw was found in curl versions from 7.59.0 through 7.61.1 in the code related to closing an easy handle. When closing and cleaning up an 'easy' handle in the `Curl_close()` function, the library code first frees a struct (without nulling the pointer) and might then subsequently erroneously write to a struct field within that already freed struct.

## References
- http://www.securitytracker.com/id/1042013
- https://security.gentoo.org/glsa/201903-03
- https://usn.ubuntu.com/3805-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16840
- https://curl.haxx.se/docs/CVE-2018-16840.html
- https://github.com/curl/curl/commit/81d135d67155c5295b1033679c606165d4e28f3f
