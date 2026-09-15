# [M] Symfony: YAML Parser Exponential Memory Allocation via Recursive Collection-Alias Expansion ("Billion Laughs")

## Summary
Severity: Medium
Advisory: CVE-2026-45304
Aliases: GHSA-4qpc-3hr4-r2p4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-45304
Type: osv

## Details
Symfony is a PHP framework for web and console applications and a set of reusable PHP components. Prior to 5.4.52, 6.4.40, 7.4.12, and 8.0.12, Symfony\Component\Yaml\Parser resolved YAML collection aliases recursively, allowing a small untrusted YAML input to expand into a multi-gigabyte structure and exhaust memory. This issue is fixed in versions 5.4.52, 6.4.40, 7.4.12, and 8.0.12.

## References
- https://github.com/symfony/symfony/releases/tag/v5.4.52
- https://github.com/symfony/symfony/releases/tag/v6.4.40
- https://github.com/symfony/symfony/releases/tag/v7.4.12
- https://github.com/symfony/symfony/releases/tag/v8.0.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45304.json
- https://github.com/symfony/symfony/security/advisories/GHSA-4qpc-3hr4-r2p4
- https://nvd.nist.gov/vuln/detail/CVE-2026-45304
- https://github.com/symfony/symfony/commit/e77391b2e4f18821198f010d573674c8ed4a970a
