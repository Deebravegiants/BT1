# [M] CVE-2019-11747

## Summary
Severity: Medium
Advisory: CVE-2019-11747
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/CVE-2019-11747
Type: osv

## Details
The "Forget about this site" feature in the History pane is intended to remove all saved user data that indicates a user has visited a site. This includes removing any HTTP Strict Transport Security (HSTS) settings received from sites that use it. Due to a bug, sites on the pre-load list also have their HSTS setting removed. On the next visit to that site if the user specifies an http: URL rather than secure https: they will not be protected by the pre-loaded HSTS setting. After that visit the site's HSTS setting will be restored. This vulnerability affects Firefox < 69 and Firefox ESR < 68.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00017.html
- https://www.mozilla.org/security/advisories/mfsa2019-25/
- https://www.mozilla.org/security/advisories/mfsa2019-26/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1564481
