# [H] CVE-2025-48050

## Summary
Severity: High
Advisory: CVE-2025-48050
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2025-05-15
Source: https://osv.dev/vulnerability/CVE-2025-48050
Type: osv

## Details
In DOMPurify through 3.2.5 before 6bc6d60, scripts/server.js does not ensure that a pathname is located under the current working directory. NOTE: the Supplier disputes the significance of this report because the "Uncontrolled data used in path expression" occurs "in a development helper script which starts a local web server if needed and must be manually started."

## References
- https://security.snyk.io/vuln/SNYK-JS-DOMPURIFY-10176060
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48050.json
- https://github.com/odaysec/advisory/blob/main/cure53/DOMPurify/writeup.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-48050
- https://github.com/cure53/DOMPurify/commit/6bc6d60e49256f27a4022181b7d8a5b0721fd534
- https://github.com/cure53/DOMPurify/pull/1101
