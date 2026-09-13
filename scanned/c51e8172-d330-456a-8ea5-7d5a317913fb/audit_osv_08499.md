# [H] CVE-2016-3958

## Summary
Severity: High
Advisory: CVE-2016-3958
Aliases: GO-2021-0163
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-3958
Type: osv

## Details
Untrusted search path vulnerability in Go before 1.5.4 and 1.6.x before 1.6.1 on Windows allows local users to gain privileges via a Trojan horse DLL in the current working directory, related to use of the LoadLibrary function.

## References
- https://groups.google.com/forum/#%21topic/golang-announce/9eqIHqaWvck
- http://www.openwall.com/lists/oss-security/2016/04/05/1
- http://www.openwall.com/lists/oss-security/2016/04/05/2
- https://github.com/golang/go/issues/14959
- https://go-review.googlesource.com/#/c/21428/
