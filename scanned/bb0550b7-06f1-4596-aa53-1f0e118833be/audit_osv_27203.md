# [H] Denial of Service in aimhubio/aim

## Summary
Severity: High
Advisory: CVE-2024-12778
Aliases: GHSA-35p3-6j45-prwm, PYSEC-2026-1080
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12778
Type: osv

## Details
A vulnerability in aimhubio/aim version 3.25.0 allows for a denial of service (DoS) attack. The issue arises when a large number of tracked metrics are retrieved simultaneously from the Aim web API, causing the web server to become unresponsive. The root cause is the lack of a limit on the number of metrics that can be requested per call, combined with the server's single-threaded nature, leading to excessive resource consumption and blocking of the server.

## References
- https://huntr.com/bounties/892a9eee-0251-4e57-94a4-dad2e7f32715
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12778.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12778
