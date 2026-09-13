# [M] CVE-2020-15676

## Summary
Severity: Medium
Advisory: CVE-2020-15676
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-10-01
Source: https://osv.dev/vulnerability/CVE-2020-15676
Type: osv

## Details
Firefox sometimes ran the onload handler for SVG elements that the DOM sanitizer decided to remove, resulting in JavaScript being executed after pasting attacker-controlled data into a contenteditable element. This vulnerability affects Firefox < 81, Thunderbird < 78.3, and Firefox ESR < 78.3.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-44/
- https://security.gentoo.org/glsa/202010-02
- https://www.debian.org/security/2020/dsa-4770
- https://www.mozilla.org/security/advisories/mfsa2020-42/
- https://www.mozilla.org/security/advisories/mfsa2020-43/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00074.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00077.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00020.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1646140
