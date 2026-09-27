# [M] CVE-2023-6209

## Summary
Severity: Medium
Advisory: CVE-2023-6209
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-6209
Type: osv

## Details
Relative URLs starting with three slashes were incorrectly parsed, and a path-traversal "/../" part in the path could be used to override the specified host. This could contribute to security problems in web sites. This vulnerability affects Firefox < 120, Firefox ESR < 115.5.0, and Thunderbird < 115.5.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00030.html
- https://www.mozilla.org/security/advisories/mfsa2023-49/
- https://www.mozilla.org/security/advisories/mfsa2023-50/
- https://www.mozilla.org/security/advisories/mfsa2023-52/
- https://www.debian.org/security/2023/dsa-5561
- https://bugzilla.mozilla.org/show_bug.cgi?id=1858570
- https://lists.debian.org/debian-lts-announce/2023/11/msg00017.html
