# [C] Session Fixation in ipsilon

## Summary
Severity: Critical
Advisory: GHSA-376m-3rm2-9jm6
CVE: CVE-2016-8638
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-376m-3rm2-9jm6
Type: github-advisory

## Affected
- PyPI: `ipsilon` — affected >=2.0.0 <2.0.2
- PyPI: `ipsilon` — affected >=1.2.0 <1.2.1
- PyPI: `ipsilon` — affected >=1.1.0 <1.1.2
- PyPI: `ipsilon` — affected >=1.0.0 <1.0.3

## Details
A vulnerability in ipsilon 2.0 before 2.0.2, 1.2 before 1.2.1, 1.1 before 1.1.2, and 1.0 before 1.0.3 was found that allows attacker to log out active sessions of other users.  This issue is related to how it tracks sessions, and allows an unauthenticated attacker to view and terminate active sessions from other users. It is also called a "SAML2 multi-session vulnerability."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8638
- https://github.com/ipsilon-project/ipsilon/commit/1c48414877fc110652b6078a29529972c7ec9122
- https://github.com/ipsilon-project/ipsilon/commit/64fc366c054fc6af1d9d2692902db169884b5f78
- https://github.com/ipsilon-project/ipsilon/commit/a33303b6beb5c316d7c18b23566b7666a4e307a4
- https://github.com/ipsilon-project/ipsilon/commit/b4744a92d4fa7f6d7ade0ae2d99a2dc0ea94734d
- https://access.redhat.com/errata/RHSA-2016:2809
- https://access.redhat.com/security/cve/CVE-2016-8638
- https://bugzilla.redhat.com/show_bug.cgi?id=1392829
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8638
- https://github.com/ipsilon-project/ipsilon
- https://ipsilon-project.org/advisory/CVE-2016-8638.txt
- https://ipsilon-project.org/release/2.1.0.html
- https://pagure.io/ipsilon/c/511fa8b7001c2f9a42301aa1d4b85aaf170a461c
- http://rhn.redhat.com/errata/RHSA-2016-2809.html
- http://www.securityfocus.com/bid/94439
