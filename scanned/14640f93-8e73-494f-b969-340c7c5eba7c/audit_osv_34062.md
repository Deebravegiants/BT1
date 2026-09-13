# [C] FreeScout's deserialization of untrusted data leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-54366
Aliases: GHSA-vcc2-6r66-gvvj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-26
Source: https://osv.dev/vulnerability/CVE-2025-54366
Type: osv

## Details
FreeScout is a lightweight free open source help desk and shared inbox built with PHP (Laravel framework). In versions 1.8.185 and below, there is a critical deserialization vulnerability in the /conversation/ajax endpoint that allows authenticated users with knowledge of the APP_KEY to achieve remote code execution. The vulnerability occurs when the application processes the attachments_all and attachments POST parameters through the insecure Helper::decrypt() function, which performs unsafe deserialization of user-controlled data without proper validation. This flaw enables attackers to create arbitrary objects and manipulate their properties, leading to complete compromise of the web application. This is fixed in version 1.8.186.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54366.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-vcc2-6r66-gvvj
- https://nvd.nist.gov/vuln/detail/CVE-2025-54366
- https://github.com/freescout-help-desk/freescout/commit/9669c57f1ddbee896752d9e16270abfd97b20eb9
