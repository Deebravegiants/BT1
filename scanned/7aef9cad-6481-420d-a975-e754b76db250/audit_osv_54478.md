# [M] CVE-2023-6867

## Summary
Severity: Medium
Advisory: CVE-2023-6867
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6867
Type: osv

## Details
The timing of a button click causing a popup to disappear was approximately the same length as the anti-clickjacking delay on permission prompts. It was possible to use this fact to surprise users by luring them to click where the permission grant button would be about to appear. This vulnerability affects Firefox ESR < 115.6 and Firefox < 121.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00020.html
- https://security.gentoo.org/glsa/202401-10
- https://www.debian.org/security/2023/dsa-5581
- https://www.mozilla.org/security/advisories/mfsa2023-54/
- https://www.mozilla.org/security/advisories/mfsa2023-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1863863
