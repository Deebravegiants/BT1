# [C] AVideo < 20.1 ImageGallery Plugin Unauthenticated File Upload and Deletion

## Summary
Severity: Critical
Advisory: CVE-2025-34434
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-34434
Type: osv

## Details
AVideo versions prior to 20.1 with the ImageGallery plugin enabled is vulnerable to unauthenticated file upload and deletion. Plugin endpoints responsible for managing gallery images fail to enforce authentication checks and do not validate ownership, allowing unauthenticated attackers to upload or delete images associated with any image-based video.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34434.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34434
- https://www.vulncheck.com/advisories/avideo-imagegallery-plugin-unauthenticated-file-upload-and-deletion
- https://github.com/WWBN/AVideo/commit/4a53ab2056
- https://github.com/WWBN/AVideo/commit/c279999cbd
- https://chocapikk.com/posts/2025/avideo-security-vulnerabilities/
