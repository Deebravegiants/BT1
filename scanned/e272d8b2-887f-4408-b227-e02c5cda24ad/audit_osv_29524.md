# [M] CVE-2024-4367

## Summary
Severity: Medium
Advisory: CVE-2024-4367
Aliases: GHSA-wgrm-67xf-hhpq
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/CVE-2024-4367
Type: osv

## Details
A type check was missing when handling fonts in PDF.js, which would allow arbitrary JavaScript execution in the PDF.js context. This vulnerability affects Firefox < 126, Firefox ESR < 115.11, and Thunderbird < 115.11.

## References
- http://seclists.org/fulldisclosure/2024/Aug/30
- https://cert-portal.siemens.com/productcert/html/ssa-827383.html
- https://github.com/mozilla/pdf.js/releases/tag/v4.2.67
- https://lists.debian.org/debian-lts-announce/2024/05/msg00010.html
- https://lists.debian.org/debian-lts-announce/2024/05/msg00012.html
- https://www.exploit-db.com/exploits/52273
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4367.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4367
- https://www.mozilla.org/security/advisories/mfsa2024-21/
- https://www.mozilla.org/security/advisories/mfsa2024-22/
- https://www.mozilla.org/security/advisories/mfsa2024-23/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1893645
- https://github.com/gogs/gogs/issues/7928
- https://codeanlabs.com/blog/research/cve-2024-4367-arbitrary-js-execution-in-pdf-js/
