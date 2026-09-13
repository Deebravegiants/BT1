# [H] CVE-2020-15678

## Summary
Severity: High
Advisory: CVE-2020-15678
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-10-01
Source: https://osv.dev/vulnerability/CVE-2020-15678
Type: osv

## Details
When recursing through graphical layers while scrolling, an iterator may have become invalid, resulting in a potential use-after-free. This occurs because the function APZCTreeManager::ComputeClippedCompositionBounds did not follow iterator invalidation rules. This vulnerability affects Firefox < 81, Thunderbird < 78.3, and Firefox ESR < 78.3.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-42/
- https://www.mozilla.org/security/advisories/mfsa2020-44/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00074.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00077.html
- https://www.mozilla.org/security/advisories/mfsa2020-43/
- https://lists.debian.org/debian-lts-announce/2020/10/msg00020.html
- https://security.gentoo.org/glsa/202010-02
- https://www.debian.org/security/2020/dsa-4770
- https://bugzilla.mozilla.org/show_bug.cgi?id=1660211
