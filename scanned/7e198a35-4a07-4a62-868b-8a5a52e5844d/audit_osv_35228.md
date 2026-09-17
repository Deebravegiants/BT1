# [M] CVE-2025-69581

## Summary
Severity: Medium
Advisory: CVE-2025-69581
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2025-69581
Type: osv

## Details
An issue was discovered in Chamillo LMS 1.11.2. The Social Network /personal_data endpoint exposes full sensitive user information even after logout because proper cache-control is missing. Using the browser back button restores all personal data, allowing unauthorized users on the same device to view confidential information. This leads to profiling, impersonation, targeted attacks, and significant privacy risks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69581.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69581
- https://github.com/Rivek619/CVE-2025-69581
- https://github.com/chamilo/chamilo-lms
