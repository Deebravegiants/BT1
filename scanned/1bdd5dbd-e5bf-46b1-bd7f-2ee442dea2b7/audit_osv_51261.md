# [M] CVE-2021-23968

## Summary
Severity: Medium
Advisory: CVE-2021-23968
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-23968
Type: osv

## Details
If Content Security Policy blocked frame navigation, the full destination of a redirect served in the frame was reported in the violation report; as opposed to the original frame URI. This could be used to leak sensitive information contained in such URIs. This vulnerability affects Firefox < 86, Thunderbird < 78.8, and Firefox ESR < 78.8.

## References
- https://lists.debian.org/debian-lts-announce/2021/03/msg00000.html
- https://security.gentoo.org/glsa/202104-09
- https://security.gentoo.org/glsa/202104-10
- https://www.debian.org/security/2021/dsa-4866
- https://www.mozilla.org/security/advisories/mfsa2021-07/
- https://www.mozilla.org/security/advisories/mfsa2021-08/
- https://www.mozilla.org/security/advisories/mfsa2021-09/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1687342
