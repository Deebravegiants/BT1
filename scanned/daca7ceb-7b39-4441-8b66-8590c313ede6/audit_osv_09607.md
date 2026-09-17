# [H] CVE-2017-1000381

## Summary
Severity: High
Advisory: CVE-2017-1000381
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/CVE-2017-1000381
Type: osv

## Details
The c-ares function `ares_parse_naptr_reply()`, which is used for parsing NAPTR responses, could be triggered to read memory outside of the given input buffer if the passed in DNS response packet was crafted in a particular way.

## References
- http://www.securityfocus.com/bid/99148
- https://c-ares.haxx.se/0616.patch
- https://c-ares.haxx.se/adv_20170620.html
