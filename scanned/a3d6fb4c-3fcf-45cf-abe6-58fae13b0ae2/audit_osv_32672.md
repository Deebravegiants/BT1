# [C] AVideo < 20.1 IDOR Arbitrary File Deletion

## Summary
Severity: Critical
Advisory: CVE-2025-34435
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-34435
Type: osv

## Details
AVideo versions prior to 20.1 are vulnerable to an insecure direct object reference (IDOR) that allows any authenticated user to delete media files belonging to other users. The affected endpoint validates authentication but fails to verify ownership or edit permissions for the targeted video.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34435.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34435
- https://www.vulncheck.com/advisories/avideo-idor-arbitrary-file-deletion
- https://github.com/WWBN/AVideo/commit/275a54268b
- https://github.com/WWBN/AVideo/commit/4a53ab2056
- https://chocapikk.com/posts/2025/avideo-security-vulnerabilities/
