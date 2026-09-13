# [H] CVE-2018-12397

## Summary
Severity: High
Advisory: CVE-2018-12397
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2018-12397
Type: osv

## Details
A WebExtension can request access to local files without the warning prompt stating that the extension will "Access your data for all websites" being displayed to the user. This allows extensions to run content scripts in local pages without permission warnings when a local file is opened. This vulnerability affects Firefox ESR < 60.3 and Firefox < 63.

## References
- https://security.gentoo.org/glsa/201811-04
- https://usn.ubuntu.com/3801-1/
- http://www.securityfocus.com/bid/105718
- https://access.redhat.com/errata/RHSA-2018:3006
- https://www.debian.org/security/2018/dsa-4324
- https://www.mozilla.org/security/advisories/mfsa2018-26/
- https://www.mozilla.org/security/advisories/mfsa2018-27/
- http://www.securitytracker.com/id/1041944
- https://access.redhat.com/errata/RHSA-2018:3005
- https://lists.debian.org/debian-lts-announce/2018/11/msg00008.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1487478
