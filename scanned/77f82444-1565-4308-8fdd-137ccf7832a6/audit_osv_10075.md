# [H] CVE-2017-13083

## Summary
Severity: High
Advisory: CVE-2017-13083
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-13083
Type: osv

## Details
Akeo Consulting Rufus prior to version 2.17.1187 does not adequately validate the integrity of updates downloaded over HTTP, allowing an attacker to easily convince a user to execute arbitrary code

## References
- http://www.kb.cert.org/vuls/id/403768
- http://www.securityfocus.com/bid/100516
- https://github.com/pbatard/rufus/commit/c3c39f7f8a11f612c4ebf7affce25ec6928eb1cb
- https://github.com/pbatard/rufus/issues/1009
