# [M] Gokapi vulnerable to stored XSS via uploading file with malicious file name

## Summary
Severity: Medium
Advisory: GHSA-95rc-wc32-gm53
CVE: CVE-2025-48494
CWE: CWE-79, CWE-87
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-06-03
Source: https://github.com/advisories/GHSA-95rc-wc32-gm53
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=1.0.1
- Go: `github.com/forceu/gokapi` — affected >=0 <0.0.0-20250530191232-343cc566cfd7

## Details
### Impact

When using end-to-end encryption, a stored XSS vulnerability can be exploited by uploading a file with JavaScript code embedded in the filename. After upload and every time someone opens the upload list, the script is then parsed.

With the affected versions <v2.0, there was no user permission system implemented, therefore all authenticated users were already able to see and modify all resources, even if end-to-end encrypted, as the encryption key had to be the same for all users with <v2.0. Nethertheless with XSS, other attack vectors like redirection or crypto mining would be possble.

### Patches

This CVE has been fixed in v2.0.0

### Workarounds

If you are the only authenticated user using Gokapi, you are not affected. A workaround would be to disable end-to-end encryption.

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-95rc-wc32-gm53
- https://nvd.nist.gov/vuln/detail/CVE-2025-48494
- https://github.com/Forceu/Gokapi/commit/343cc566cfd7f4efcd522c92371561d494aed6b0
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.0.0
- https://pkg.go.dev/vuln/GO-2025-3737
