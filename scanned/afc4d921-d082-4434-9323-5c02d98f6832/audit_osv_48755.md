# [H] CVE-2018-12395

## Summary
Severity: High
Advisory: CVE-2018-12395
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2018-12395
Type: osv

## Details
By rewriting the Host: request headers using the webRequest API, a WebExtension can bypass domain restrictions through domain fronting. This would allow access to domains that share a host that are otherwise restricted. This vulnerability affects Firefox ESR < 60.3 and Firefox < 63.

## References
- http://www.securitytracker.com/id/1041944
- https://access.redhat.com/errata/RHSA-2018:3005
- https://lists.debian.org/debian-lts-announce/2018/11/msg00008.html
- https://security.gentoo.org/glsa/201811-04
- https://www.mozilla.org/security/advisories/mfsa2018-26/
- http://www.securityfocus.com/bid/105718
- https://access.redhat.com/errata/RHSA-2018:3006
- https://usn.ubuntu.com/3801-1/
- https://www.debian.org/security/2018/dsa-4324
- https://www.mozilla.org/security/advisories/mfsa2018-27/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1467523
