# [M] CVE-2019-11742

## Summary
Severity: Medium
Advisory: CVE-2019-11742
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/CVE-2019-11742
Type: osv

## Details
A same-origin policy violation occurs allowing the theft of cross-origin images through a combination of SVG filters and a &lt;canvas&gt; element due to an error in how same-origin policy is applied to cached image content. The resulting same-origin policy violation could allow for data theft. This vulnerability affects Firefox < 69, Thunderbird < 68.1, Thunderbird < 60.9, Firefox ESR < 60.9, and Firefox ESR < 68.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00011.html
- https://usn.ubuntu.com/4150-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00017.html
- https://security.gentoo.org/glsa/201911-07
- https://www.mozilla.org/security/advisories/mfsa2019-26/
- https://www.mozilla.org/security/advisories/mfsa2019-27/
- https://www.mozilla.org/security/advisories/mfsa2019-29/
- https://www.mozilla.org/security/advisories/mfsa2019-25/
- https://www.mozilla.org/security/advisories/mfsa2019-30/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1559715
