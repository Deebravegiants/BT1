# [H] CVE-2017-5386

## Summary
Severity: High
Advisory: CVE-2017-5386
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5386
Type: osv

## Details
WebExtension scripts can use the "data:" protocol to affect pages loaded by other web extensions using this protocol, leading to potential data disclosure or privilege escalation in affected extensions. This vulnerability affects Firefox ESR < 45.7 and Firefox < 51.

## References
- https://www.mozilla.org/security/advisories/mfsa2017-01/
- https://www.mozilla.org/security/advisories/mfsa2017-02/
- http://rhn.redhat.com/errata/RHSA-2017-0190.html
- http://www.securityfocus.com/bid/95769
- http://www.securitytracker.com/id/1037693
- https://security.gentoo.org/glsa/201702-22
- https://www.debian.org/security/2017/dsa-3771
- https://bugzilla.mozilla.org/show_bug.cgi?id=1319070
