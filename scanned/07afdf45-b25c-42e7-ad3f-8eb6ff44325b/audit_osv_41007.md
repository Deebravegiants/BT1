# [M] Adminer before 5.4.3 Unrestricted File Upload via AdminerFileUpload

## Summary
Severity: Medium
Advisory: CVE-2026-56702
Aliases: GHSA-vcvj-rwwm-x6g5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-56702
Type: osv

## Details
Adminer versions before 5.4.3 contain an unrestricted file upload vulnerability in the AdminerFileUpload plugin that allows authenticated users to upload PHP files by exploiting a permissive default extension allowlist. Attackers can upload PHP webshells to columns ending in _path and execute arbitrary code as the web-server user when uploadPath is web-served.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56702.json
- https://github.com/vrana/adminer/security/advisories/GHSA-vcvj-rwwm-x6g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-56702
- https://www.vulncheck.com/advisories/adminer-before-unrestricted-file-upload-via-adminerfileupload
