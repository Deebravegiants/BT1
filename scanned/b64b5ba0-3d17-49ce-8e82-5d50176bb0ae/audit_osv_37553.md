# [M] WeGIA affected by arbitrary file read via symlink in backup restore

## Summary
Severity: Medium
Advisory: CVE-2026-31894
Aliases: GHSA-6mmm-27h8-8g55
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31894
Type: osv

## Details
WeGIA is a web manager for charitable institutions. In 3.6.5, The patched loadBackupDB() extracts tar.gz archives to a temporary directory using PHP's PharData class, then uses glob() and file_get_contents() to read SQL files from the extracted contents. Neither the extraction nor the file reading validates whether archive members are symbolic links. This vulnerability is fixed in 3.6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31894.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-6mmm-27h8-8g55
- https://nvd.nist.gov/vuln/detail/CVE-2026-31894
- https://github.com/LabRedesCefetRJ/WeGIA/commit/79e7a164eddb527e3b331037b7a4defb8c115d50
