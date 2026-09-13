# [M] CVE-2025-43929

## Summary
Severity: Medium
Advisory: CVE-2025-43929
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-04-20
Source: https://osv.dev/vulnerability/CVE-2025-43929
Type: osv

## Details
open_actions.py in kitty before 0.41.0 does not ask for user confirmation before running a local executable file that may have been linked from an untrusted document (e.g., a document opened in KDE ghostwriter).

## References
- https://ghostwriter.kde.org/documentation/#links
- https://github.com/kovidgoyal/kitty/compare/v0.40.1...v0.41.0
- https://hitman.services/cve-2025-43929/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/43xxx/CVE-2025-43929.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-43929
- https://github.com/kovidgoyal/kitty/commit/ce5cfdd9caf44c538af800a07162e1f49bd53c35
- https://github.com/0xBenCantCode/CVE-2025-43929
