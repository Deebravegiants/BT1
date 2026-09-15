# [M] CVE-2025-65519

## Summary
Severity: Medium
Advisory: CVE-2025-65519
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2025-65519
Type: osv

## Details
mayswind ezbookkeeping versions 1.2.0 and earlier contain a critical vulnerability in JSON and XML file import processing. The application fails to validate nesting depth during parsing operations, allowing authenticated attackers to trigger denial of service conditions by uploading deeply nested malicious files. This results in CPU exhaustion, service degradation, or complete service unavailability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65519.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65519
- https://github.com/ictrun/EBK-SA-2025-001
