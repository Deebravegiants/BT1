# [C] AVideo < 20.1 IDOR Arbitrary Comment Image Upload

## Summary
Severity: Critical
Advisory: CVE-2025-34437
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-34437
Type: osv

## Details
AVideo versions prior to 20.1 permit any authenticated user to upload comment images to videos owned by other users. The endpoint validates authentication but omits ownership checks, allowing attackers to perform unauthorized uploads to arbitrary video objects.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34437.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34437
- https://www.vulncheck.com/advisories/avideo-idor-arbitrary-comment-image-upload
- https://github.com/WWBN/AVideo/commit/4a53ab2056
- https://github.com/WWBN/AVideo/commit/d411f91805
- https://chocapikk.com/posts/2025/avideo-security-vulnerabilities/
