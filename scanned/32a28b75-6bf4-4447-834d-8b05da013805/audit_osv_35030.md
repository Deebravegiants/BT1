# [H] Myhoard logs backup encryption key in plain text

## Summary
Severity: High
Advisory: CVE-2025-67745
Aliases: GHSA-v42r-6hr9-4hcr
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-67745
Type: osv

## Details
MyHoard is a daemon for creating, managing and restoring MySQL backups. Starting in version 1.0.1 and prior to version 1.3.0, in some cases, myhoard logs the whole backup info, including the encryption key. Version 1.3.0 fixes the issue. As a workaround, direct logs into /dev/null.

## References
- https://github.com/Aiven-Open/myhoard/security/advisories/GHSA-v42r-6hr9-4hcr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67745.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67745
- https://github.com/Aiven-Open/myhoard/commit/fac89793bfc8c81ae040aadf5292f5d0100b6640
