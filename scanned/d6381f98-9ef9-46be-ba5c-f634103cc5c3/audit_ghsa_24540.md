# [H] Malicious PDF can inject JavaScript into PDF Viewer

## Summary
Severity: High
Advisory: GHSA-7jg2-jgv3-fmr4
CVE: CVE-2018-5158
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7jg2-jgv3-fmr4
Type: github-advisory

## Affected
- npm: `pdfjs-dist` — affected >=2.0.0 <2.0.550
- npm: `pdfjs-dist` — affected >=0 <1.10.100

## Details
The PDF viewer does not sufficiently sanitize PostScript calculator functions, allowing malicious JavaScript to be injected through a crafted PDF file. This JavaScript can then be run with the permissions of the PDF viewer by its worker. This vulnerability affects Firefox ESR < 52.8, Firefox < 60 and PDF.js < 2.0.550.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5158
- https://github.com/mozilla/pdf.js/pull/9659
- https://github.com/mozilla/pdf.js/commit/2dc4af525d1612c98afcd1e6bee57d4788f78f97
- https://access.redhat.com/errata/RHSA-2018:1414
- https://access.redhat.com/errata/RHSA-2018:1415
- https://bugzilla.mozilla.org/show_bug.cgi?id=1452075
- https://github.com/mozilla/pdf.js
- https://lists.debian.org/debian-lts-announce/2018/05/msg00007.html
- https://security.gentoo.org/glsa/201810-01
- https://usn.ubuntu.com/3645-1
- https://www.debian.org/security/2018/dsa-4199
- https://www.mozilla.org/security/advisories/mfsa2018-11
- https://www.mozilla.org/security/advisories/mfsa2018-12
- http://www.securityfocus.com/bid/104136
- http://www.securitytracker.com/id/1040896
