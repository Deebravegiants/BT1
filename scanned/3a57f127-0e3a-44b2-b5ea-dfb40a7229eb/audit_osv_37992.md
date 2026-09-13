# [H] Chamilo LMS: Unauthenticated SSRF via PENS Plugin allows attacker to probe internal network and reach cloud metadata services

## Summary
Severity: High
Advisory: CVE-2026-34160
Aliases: GHSA-g2xj-4cch-j276
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-34160
Type: osv

## Details
Chamilo LMS is an open-source learning management system. In versions prior to 2.0.0-RC.3, the PENS (Package Exchange Notification Services) plugin endpoint at public/plugin/Pens/pens.php is accessible without authentication and accepts a user-controlled package-url parameter that the server fetches using curl without filtering private or internal IP addresses, enabling unauthenticated Server-Side Request Forgery (SSRF). An attacker can exploit this to probe internal network services, access cloud metadata endpoints (such as 169.254.169.254) to steal IAM credentials and sensitive instance metadata, or trigger state-changing operations on internal services via the receipt and alerts callback parameters. No authentication is required to exploit either SSRF vector, significantly increasing the attack surface. This issue has been fixed in version 2.0.0-RC.3.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v2.0.0-RC.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34160.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-g2xj-4cch-j276
- https://nvd.nist.gov/vuln/detail/CVE-2026-34160
- https://github.com/chamilo/chamilo-lms/commit/de4058d76fac2413afd023b1ec942e8e79579011
