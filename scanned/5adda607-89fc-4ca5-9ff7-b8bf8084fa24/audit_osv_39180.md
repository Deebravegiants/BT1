# [C] CubeCart: Server-Side Template Injection (SSTI) in Smarty Templates leading to RCE

## Summary
Severity: Critical
Advisory: CVE-2026-44377
Aliases: GHSA-wpjx-g695-qc5j
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44377
Type: osv

## Details
CubeCart is an ecommerce software solution. Prior to 6.7.0, an Authenticated Server-Side Template Injection (SSTI) vulnerability exists in multiple modules of CubeCart (including Email Templates and Documents). The application unsafely evaluates user-supplied input directly through the Smarty template engine. By leveraging this, an authenticated attacker with administrative privileges can bypass current restrictions and call native PHP functions within the templates, such as readgzfile() to read sensitive configuration files, or error_log() to write a malicious PHP web shell, ultimately achieving Information Disclosure and full Remote Code Execution (RCE). This vulnerability is fixed in 6.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44377.json
- https://github.com/cubecart/v6/security/advisories/GHSA-wpjx-g695-qc5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-44377
- https://github.com/cubecart/v6/commit/76d783c8c4d87a8a90dbfef1344a2733e7c6434c
