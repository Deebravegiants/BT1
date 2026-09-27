# [M] Symfony: YAML Parser ReDoS via Catastrophic Backtracking in Parser::cleanup() Regex

## Summary
Severity: Medium
Advisory: CVE-2026-45305
Aliases: GHSA-9frc-8383-795m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-45305
Type: osv

## Details
Symfony is a PHP framework for web and console applications and a set of reusable PHP components. Prior to 5.4.52, 6.4.40, 7.4.12, and 8.0.12, Symfony\Component\Yaml\Parser::cleanup() used regular expressions with overlapping quantifiers for YAML directive, comment, and document marker cleanup, allowing crafted input to make parsing hang for an arbitrarily long time. This issue is fixed in versions 5.4.52, 6.4.40, 7.4.12, and 8.0.12.

## References
- https://github.com/symfony/symfony/releases/tag/v5.4.52
- https://github.com/symfony/symfony/releases/tag/v6.4.40
- https://github.com/symfony/symfony/releases/tag/v7.4.12
- https://github.com/symfony/symfony/releases/tag/v8.0.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45305.json
- https://github.com/symfony/symfony/security/advisories/GHSA-9frc-8383-795m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45305
- https://github.com/symfony/symfony/commit/9749cd43c5e09b3735093623670b21b9d8a056cb
