# [M] CVE-2023-6860

## Summary
Severity: Medium
Advisory: CVE-2023-6860
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6860
Type: osv

## Details
The `VideoBridge` allowed any content process to use textures produced by remote decoders.  This could be abused to escape the sandbox. This vulnerability affects Firefox ESR < 115.6, Thunderbird < 115.6, and Firefox < 121.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00020.html
- https://security.gentoo.org/glsa/202401-10
- https://www.debian.org/security/2023/dsa-5582
- https://lists.debian.org/debian-lts-announce/2023/12/msg00021.html
- https://www.debian.org/security/2023/dsa-5581
- https://www.mozilla.org/security/advisories/mfsa2023-54/
- https://www.mozilla.org/security/advisories/mfsa2023-55/
- https://www.mozilla.org/security/advisories/mfsa2023-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1854669
