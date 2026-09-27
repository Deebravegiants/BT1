# [H] CVE-2019-17005

## Summary
Severity: High
Advisory: CVE-2019-17005
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-17005
Type: osv

## Details
The plain text serializer used a fixed-size array for the number of <ol> elements it could process; however it was possible to overflow the static-sized array leading to memory corruption and a potentially exploitable crash. This vulnerability affects Thunderbird < 68.3, Firefox ESR < 68.3, and Firefox < 71.

## References
- https://security.gentoo.org/glsa/202003-10
- https://usn.ubuntu.com/4241-1/
- https://www.mozilla.org/security/advisories/mfsa2019-38/
- https://access.redhat.com/errata/RHSA-2020:0292
- https://access.redhat.com/errata/RHSA-2020:0295
- https://security.gentoo.org/glsa/202003-02
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2019-36/
- https://www.mozilla.org/security/advisories/mfsa2019-37/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00000.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1584170
