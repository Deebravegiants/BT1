# [M] phpMyFAQ before v4.1.6 Local File Disclosure via PDF Export

## Summary
Severity: Medium
Advisory: CVE-2026-76210
Aliases: GHSA-c63q-xx7x-j8w2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76210
Type: osv

## Details
phpMyFAQ before 4.1.6 does not adequately sanitize HTML in FAQ answers before generating PDFs via TCPDF. An attacker with permission to create or edit FAQ content can embed an <img> tag whose src references a local file under the web root's content/ directory (e.g., content/core/config/database.php). When the PDF is generated, phpMyFAQ attempts to read the referenced file; because it is not a valid image the resulting error is converted into an uncaught exception whose stack trace discloses part of the file's contents to any user who triggers the PDF export. By default the disclosed portion is truncated (zend.exception_string_param_max_len), but a larger configured value can result in disclosure of entire files, including database credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76210.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-c63q-xx7x-j8w2
- https://nvd.nist.gov/vuln/detail/CVE-2026-76210
- https://www.vulncheck.com/advisories/phpmyfaq-before-local-file-disclosure-via-pdf-export
