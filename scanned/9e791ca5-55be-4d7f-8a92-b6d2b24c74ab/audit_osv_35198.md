# [H] Wget2: arbitrary file write via metalink path traversal in gnu wget2

## Summary
Severity: High
Advisory: CVE-2025-69194
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-09
Source: https://osv.dev/vulnerability/CVE-2025-69194
Type: osv

## Details
A security issue was discovered in GNU Wget2 when handling Metalink documents. The application fails to properly validate file paths provided in Metalink <file name> elements. An attacker can abuse this behavior to write files to unintended locations on the system. This can lead to data loss or potentially allow further compromise of the user’s environment.

## References
- https://access.redhat.com/security/cve/CVE-2025-69194
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69194.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69194
- https://bugzilla.redhat.com/show_bug.cgi?id=2425773
- https://gitlab.com/gnuwget/wget2
