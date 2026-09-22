# [H] Cookie and header exposure in twisted

## Summary
Severity: High
Advisory: GHSA-92x2-jw7w-xvvx
CVE: CVE-2022-21712
CWE: CWE-200, CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-07
Source: https://github.com/advisories/GHSA-92x2-jw7w-xvvx
Type: github-advisory

## Affected
- PyPI: `Twisted` — affected >=11.1.0 <22.1.0

## Details
### Impact

Cookie and Authorization headers are leaked when following cross-origin redirects in `twited.web.client.RedirectAgent` and `twisted.web.client.BrowserLikeRedirectAgent`.

## References
- https://github.com/twisted/twisted/security/advisories/GHSA-92x2-jw7w-xvvx
- https://nvd.nist.gov/vuln/detail/CVE-2022-21712
- https://github.com/twisted/twisted/commit/af8fe78542a6f2bf2235ccee8158d9c88d31e8e2
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2022-27.yaml
- https://github.com/twisted/twisted
- https://github.com/twisted/twisted/releases/tag/twisted-22.1.0
- https://lists.debian.org/debian-lts-announce/2022/02/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7U6KYDTOLPICAVSR34G2WRYLFBD2YW5K
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GLKHA6WREIVAMBQD7KKWYHPHGGNKMAG6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7U6KYDTOLPICAVSR34G2WRYLFBD2YW5K
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GLKHA6WREIVAMBQD7KKWYHPHGGNKMAG6
- https://pypi.org/project/Twisted
- https://security.gentoo.org/glsa/202301-02
