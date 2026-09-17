# [M] Microweber CMS API has authenticated local file inclusion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j64v-xh5w-8hqj
CVE: CVE-2025-34076
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-07-02
Source: https://github.com/advisories/GHSA-j64v-xh5w-8hqj
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.2.11

## Details
An authenticated local file inclusion vulnerability exists in Microweber CMS versions < 1.2.11 through misuse of the backup management API. Authenticated users can abuse the /api/BackupV2/upload and /api/BackupV2/download endpoints to read arbitrary files from the underlying filesystem. By specifying an absolute file path in the src parameter of the upload request, the server may relocate or delete the target file depending on the web service user’s privileges. The corresponding download endpoint can then be used to retrieve the file contents, effectively enabling local file disclosure. This behavior stems from insufficient validation of user-supplied paths and inadequate restrictions on file access and backup logic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-34076
- https://github.com/microweber/microweber/commit/572bdc36b5b47923790016f6b961c8df53226855
- https://github.com/microweber/microweber/commit/98d025467128ecc24195dcb56c533febc3c91af6
- https://github.com/microweber/microweber
- https://huntr.com/bounties/09218d3f-1f6a-48ae-981c-85e86ad5ed8b
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/auxiliary/gather/microweber_lfi.rb
- https://vulncheck.com/advisories/microweber-cms-lfi
