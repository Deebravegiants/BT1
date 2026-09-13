# [M] CVE-2025-46651

## Summary
Severity: Medium
Advisory: CVE-2025-46651
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2025-46651
Type: osv

## Details
Tiny File Manager through 2.6 contains a server-side request forgery (SSRF) vulnerability in the URL upload feature. Due to insufficient validation of user-supplied URLs, an attacker can send crafted requests to localhost by using http://www.127.0.0.1.example.com/ or a similarly constructed domain name. This may lead to unauthorized port scanning or access to internal-only services.

## References
- https://github.com/prasathmani/tinyfilemanager/blob/master/tinyfilemanager.php#L608
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46651.json
- https://github.com/RobertoLuzanilla/tinyfilemanager-security-advisories/blob/main/CVE-2025-46651.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-46651
