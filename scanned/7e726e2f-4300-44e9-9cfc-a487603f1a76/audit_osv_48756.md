# [M] CVE-2018-12396

## Summary
Severity: Medium
Advisory: CVE-2018-12396
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2018-12396
Type: osv

## Details
A vulnerability where a WebExtension can run content scripts in disallowed contexts following navigation or other events. This allows for potential privilege escalation by the WebExtension on sites where content scripts should not be run. This vulnerability affects Firefox ESR < 60.3 and Firefox < 63.

## References
- http://www.securityfocus.com/bid/105718
- http://www.securitytracker.com/id/1041944
- https://access.redhat.com/errata/RHSA-2018:3006
- https://lists.debian.org/debian-lts-announce/2018/11/msg00008.html
- https://security.gentoo.org/glsa/201811-04
- https://www.debian.org/security/2018/dsa-4324
- https://www.mozilla.org/security/advisories/mfsa2018-26/
- https://access.redhat.com/errata/RHSA-2018:3005
- https://usn.ubuntu.com/3801-1/
- https://www.mozilla.org/security/advisories/mfsa2018-27/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1483602
