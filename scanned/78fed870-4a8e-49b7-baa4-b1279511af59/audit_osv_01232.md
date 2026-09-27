# [H] ALPINE-CVE-2018-7032

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7032
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7032
Type: osv

## Affected
- Alpine:v3.5: `myrepos` — affected >=0 <1.20180726-r0
- Alpine:v3.6: `myrepos` — affected >=0 <1.20180726-r0
- Alpine:v3.7: `myrepos` — affected >=0 <1.20180726-r0
- Alpine:v3.8: `myrepos` — affected >=0 <1.20180726-r0

## Details
webcheckout in myrepos through 1.20171231 does not sanitize URLs that are passed to git clone, allowing a malicious website operator or a MitM attacker to take advantage of it for arbitrary code execution, as demonstrated by an "ext::sh -c" attack or an option injection attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7032
