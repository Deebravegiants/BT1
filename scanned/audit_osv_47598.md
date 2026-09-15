# [M] CVE-2016-9064

## Summary
Severity: Medium
Advisory: CVE-2016-9064
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2016-9064
Type: osv

## Details
Add-on updates failed to verify that the add-on ID inside the signed package matched the ID of the add-on being updated. An attacker who could perform a man-in-the-middle attack on the user's connection to the update server and defeat the certificate pinning protection could provide a malicious signed add-on instead of a valid update. This vulnerability affects Firefox ESR < 45.5 and Firefox < 50.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2780.html
- http://www.securityfocus.com/bid/94336
- http://www.securitytracker.com/id/1037298
- https://security.gentoo.org/glsa/201701-15
- https://www.mozilla.org/security/advisories/mfsa2016-89/
- https://www.mozilla.org/security/advisories/mfsa2016-90/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1303418
