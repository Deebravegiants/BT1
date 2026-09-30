# [C] CVE-2025-65791

## Summary
Severity: Critical
Advisory: CVE-2025-65791
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2025-65791
Type: osv

## Details
ZoneMinder v1.36.34 is vulnerable to Command Injection in web/views/image.php. The application passes unsanitized user input directly to the exec() function. NOTE: this is disputed by the Supplier because there is no unsanitized user input to web/views/image.php.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65791.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65791
- https://github.com/rishavand1/CVE-2025-65791
