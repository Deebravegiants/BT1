# [M] CVE-2025-43720

## Summary
Severity: Medium
Advisory: CVE-2025-43720
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-21
Source: https://osv.dev/vulnerability/CVE-2025-43720
Type: osv

## Details
Headwind MDM before 5.33.1 makes configuration details accessible to unauthorized users. The Configuration profile is exposed to the Observer user role, revealing the password requires to escape out of the MDM controlled device's profile.

## References
- https://github.com/h-mdm/hmdm-server/compare/v5.32.1...v5.33.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/43xxx/CVE-2025-43720.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-43720
- https://github.com/h-mdm/hmdm-server/commit/19e4a63f732c99064444df7e8c61b4f01df362e8
- https://www.periculo.co.uk/cyber-security-blog/how-our-pen-tester-found-a-critical-vulnerability-cve-2025-43720
