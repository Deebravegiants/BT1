# [H] CVE-2017-7798

## Summary
Severity: High
Advisory: CVE-2017-7798
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7798
Type: osv

## Details
The Developer Tools feature suffers from a XUL injection vulnerability due to improper sanitization of the web page source code. In the worst case, this could allow arbitrary code execution when opening a malicious page with the style editor tool. This vulnerability affects Firefox ESR < 52.3 and Firefox < 55.

## References
- https://www.debian.org/security/2017/dsa-3928
- https://www.mozilla.org/security/advisories/mfsa2017-18/
- https://www.mozilla.org/security/advisories/mfsa2017-19/
- http://www.securityfocus.com/bid/100198
- http://www.securitytracker.com/id/1039124
- https://access.redhat.com/errata/RHSA-2017:2456
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1371586%2C1372112
