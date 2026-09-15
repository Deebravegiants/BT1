# [M] CVE-2023-6865

## Summary
Severity: Medium
Advisory: CVE-2023-6865
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6865
Type: osv

## Details
`EncryptingOutputStream` was susceptible to exposing uninitialized data.  This issue could only be abused in order to write data to a local disk which may have implications for private browsing mode. This vulnerability affects Firefox ESR < 115.6 and Firefox < 121.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00020.html
- https://security.gentoo.org/glsa/202401-10
- https://www.debian.org/security/2023/dsa-5581
- https://www.mozilla.org/security/advisories/mfsa2023-54/
- https://www.mozilla.org/security/advisories/mfsa2023-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1864123
