# [C] AVideo < 20.1 IDOR Arbitrary File Upload

## Summary
Severity: Critical
Advisory: CVE-2025-34436
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-34436
Type: osv

## Details
AVideo versions prior to 20.1 allow any authenticated user to upload files into directories belonging to other users due to an insecure direct object reference. The upload functionality verifies authentication but does not enforce ownership checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34436.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34436
- https://www.vulncheck.com/advisories/avideo-idor-arbitrary-file-upload
- https://github.com/WWBN/AVideo/commit/4a53ab2056
- https://github.com/WWBN/AVideo/commit/c279999cbd
- https://chocapikk.com/posts/2025/avideo-security-vulnerabilities/
