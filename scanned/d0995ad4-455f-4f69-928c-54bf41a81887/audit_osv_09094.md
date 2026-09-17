# [H] CVE-2016-7837

## Summary
Severity: High
Advisory: CVE-2016-7837
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-09
Source: https://osv.dev/vulnerability/CVE-2016-7837
Type: osv

## Details
Buffer overflow in BlueZ 5.41 and earlier allows an attacker to execute arbitrary code via the parse_line function used in some userland utilities.

## References
- https://usn.ubuntu.com/4311-1/
- http://www.securityfocus.com/bid/95067
- https://jvn.jp/en/jp/JVN38755305/index.html
- https://git.kernel.org/pub/scm/bluetooth/bluez.git/commit/?id=8514068150759c1d6a46d4605d2351babfde1601
