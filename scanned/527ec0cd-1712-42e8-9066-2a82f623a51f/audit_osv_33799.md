# [M] Chamilo: Deserialization of untrusted data in /plugin/vchamilo/views/import.php via POST configuration_file; POST course_path; POST home_path parameters

## Summary
Severity: Medium
Advisory: CVE-2025-50198
Aliases: GHSA-jgxc-96j5-8rrr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-50198
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.30, Chamilo is vulnerable to deserialization of untrusted data in /plugin/vchamilo/views/import.php via POST configuration_file; POST course_path; POST home_path parameters. This issue has been patched in version 1.11.30.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50198.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-jgxc-96j5-8rrr
- https://nvd.nist.gov/vuln/detail/CVE-2025-50198
- https://github.com/chamilo/chamilo-lms/commit/07f7954f2dd18c4f5a307b2a6fa802d9ce36b827
- https://github.com/chamilo/chamilo-lms/commit/89c67e6630852cf94d288499e2cd6f6a06f9c6f1
- https://github.com/chamilo/chamilo-lms/commit/8bd86913a89fec084053e2c2916df19f15d03d95
