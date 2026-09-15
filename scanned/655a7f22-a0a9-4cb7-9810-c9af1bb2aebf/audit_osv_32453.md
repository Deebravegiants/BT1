# [M] CVE-2025-30344

## Summary
Severity: Medium
Advisory: CVE-2025-30344
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-03-21
Source: https://osv.dev/vulnerability/CVE-2025-30344
Type: osv

## Details
An issue was discovered in OpenSlides before 4.2.5. During login at the /system/auth/login/ endpoint, the system's response times differ depending on whether a user exists in the system. The timing discrepancy stems from the omitted hashing of the password (e.g., more than 100 milliseconds).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30344.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30344
- https://www.x41-dsec.de/lab/advisories/x41-2025-001-OpenSlides
