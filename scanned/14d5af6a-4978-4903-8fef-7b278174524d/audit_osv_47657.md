# [H] CVE-2016-9902

## Summary
Severity: High
Advisory: CVE-2016-9902
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2016-9902
Type: osv

## Details
The Pocket toolbar button, once activated, listens for events fired from it's own pages but does not verify the origin of incoming events. This allows content from other origins to fire events and inject content and commands into the Pocket context. Note: this issue does not affect users with e10s enabled. This vulnerability affects Firefox ESR < 45.6 and Firefox < 50.1.

## References
- http://www.securitytracker.com/id/1037461
- https://security.gentoo.org/glsa/201701-15
- https://www.mozilla.org/security/advisories/mfsa2016-94/
- https://www.mozilla.org/security/advisories/mfsa2016-95/
- http://rhn.redhat.com/errata/RHSA-2016-2946.html
- http://rhn.redhat.com/errata/RHSA-2016-2973.html
- http://www.securityfocus.com/bid/94885
- https://bugzilla.mozilla.org/show_bug.cgi?id=1320039
