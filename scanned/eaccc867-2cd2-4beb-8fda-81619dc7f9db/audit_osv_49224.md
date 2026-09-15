# [H] CVE-2018-7032

## Summary
Severity: High
Advisory: CVE-2018-7032
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-14
Source: https://osv.dev/vulnerability/CVE-2018-7032
Type: osv

## Details
webcheckout in myrepos through 1.20171231 does not sanitize URLs that are passed to git clone, allowing a malicious website operator or a MitM attacker to take advantage of it for arbitrary code execution, as demonstrated by an "ext::sh -c" attack or an option injection attack.

## References
- https://bugs.debian.org/840014
