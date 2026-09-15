# [M] Bolt Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-wr23-m9m2-jjf4
CVE: CVE-2017-16754
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wr23-m9m2-jjf4
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected >=0 <3.3.6

## Details
Bolt before 3.3.6 does not properly restrict access to `_profiler` routes, related to `EventListener/ProfilerListener.php` and `Provider/EventListenerServiceProvider.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16754
- https://github.com/bolt/bolt/commit/aa21787241945457a2e4abc8b079672935fe0840
- https://github.com/bolt/bolt
- https://github.com/bolt/bolt/releases/tag/v3.3.6
- http://www.securityfocus.com/bid/101777
