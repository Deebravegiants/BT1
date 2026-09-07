# [M] Piranha CMS Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cmwp-442x-3rcv
CVE: CVE-2024-55342
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-12-20
Source: https://github.com/advisories/GHSA-cmwp-442x-3rcv
Type: github-advisory

## Affected
- NuGet: `Piranha` — affected >=0

## Details
A file upload functionality in Piranha CMS 11.1 allows authenticated remote attackers to upload a crafted PDF file to /manager/media. This PDF can contain malicious JavaScript code, which is executed when a victim user opens or interacts with the PDF in their web browser, leading to a XSS vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55342
- https://github.com/PiranhaCMS/piranha.core
- https://sec-fortress.github.io/posts/articles/posts/CVE-2024-55342.html
