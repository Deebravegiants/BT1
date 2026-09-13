# [C] Hytale Modding Vulnerable to Remote Code Execution via File Upload Bypass in `FileController`

## Summary
Severity: Critical
Advisory: CVE-2026-34735
Aliases: GHSA-2xqq-6778-h4j9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34735
Type: osv

## Details
The Hytale Modding Wiki is a free service for Hytale mods to host their documentation & wikis. In version 1.2.0 and prior, the quickUpload() endpoint validates uploaded files by checking their MIME type (via PHP's finfo, which inspects file contents) but constructs the stored filename using the client-supplied file extension from getClientOriginalExtension(). These two checks are independent: an attacker can upload a file whose content passes the MIME allowlist while using a .php extension. The file is stored on the public disk and is directly accessible via URL, allowing server-side code execution. At time of publication no known patches exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34735.json
- https://github.com/HytaleModding/wiki/security/advisories/GHSA-2xqq-6778-h4j9
- https://nvd.nist.gov/vuln/detail/CVE-2026-34735
