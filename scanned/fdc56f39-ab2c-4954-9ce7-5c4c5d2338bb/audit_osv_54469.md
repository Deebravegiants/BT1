# [M] CVE-2023-6857

## Summary
Severity: Medium
Advisory: CVE-2023-6857
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6857
Type: osv

## Details
When resolving a symlink, a race may occur where the buffer passed to `readlink` may actually be smaller than necessary. 
*This bug only affects Firefox on Unix-based operating systems (Android, Linux, MacOS). Windows is unaffected.* This vulnerability affects Firefox ESR < 115.6, Thunderbird < 115.6, and Firefox < 121.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/12/msg00021.html
- https://www.debian.org/security/2023/dsa-5581
- https://www.mozilla.org/security/advisories/mfsa2023-56/
- https://security.gentoo.org/glsa/202401-10
- https://www.debian.org/security/2023/dsa-5582
- https://www.mozilla.org/security/advisories/mfsa2023-54/
- https://www.mozilla.org/security/advisories/mfsa2023-55/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1796023
