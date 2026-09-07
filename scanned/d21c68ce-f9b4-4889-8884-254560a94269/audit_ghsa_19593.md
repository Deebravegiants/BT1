# [C] DevDojo Voyager Argument Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-qq2h-m2hj-hrff
CVE: CVE-2025-32931
CWE: CWE-88
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-14
Source: https://github.com/advisories/GHSA-qq2h-m2hj-hrff
Type: github-advisory

## Affected
- Packagist: `tcg/voyager` — affected >=1.4.0

## Details
DevDojo Voyager 1.4.0 through 1.8.0, when Laravel 8 or later is used, allows authenticated administrators to execute arbitrary OS commands via a specific php artisan command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-32931
- https://github.com/lishihihi/voyager-issue-report
- https://github.com/thedevdojo/voyager
- https://github.com/thedevdojo/voyager/blob/1.8/docs/core-concepts/compass.md
- https://github.com/thedevdojo/voyager/blob/7e7e0f4f0e115d2d9e0481a86153a1ceff194c00/resources/views/compass/includes/commands.blade.php#L11-L16
