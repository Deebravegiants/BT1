# [H] Chamilo LMS has Weak REST API Key Generation (Predictable)

## Summary
Severity: High
Advisory: CVE-2026-33710
Aliases: GHSA-rpmg-j327-mr39
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33710
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38 and 2.0.0-RC.3, REST API keys are generated using md5(time() + (user_id * 5) - rand(10000, 10000)). The rand(10000, 10000) call always returns exactly 10000 (min == max), making the formula effectively md5(timestamp + user_id*5 - 10000). An attacker who knows a username and approximate key creation time can brute-force the API key. This vulnerability is fixed in 1.11.38 and 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33710.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-rpmg-j327-mr39
- https://nvd.nist.gov/vuln/detail/CVE-2026-33710
- https://github.com/chamilo/chamilo-lms/commit/4448701bb8ec557e94ef02d19c72cbe9c49c2d09
- https://github.com/chamilo/chamilo-lms/commit/e7400dd840586ae134b286d0a2374f3d269a9a9d
