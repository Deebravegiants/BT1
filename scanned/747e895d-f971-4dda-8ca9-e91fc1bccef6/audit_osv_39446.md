# [M] Symfony: JsonPath Evaluates Attacker-Controlled Regular Expressions in match()/search() Without Limits — ReDoS

## Summary
Severity: Medium
Advisory: CVE-2026-45756
Aliases: GHSA-8v8v-g73j-492j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-45756
Type: osv

## Details
Symfony is a PHP framework for web and console applications and a set of reusable PHP components. From 7.3.0-BETA1 until 7.4.12 and 8.0.12, the JsonPath component compiles attacker-controlled match() and search() filter patterns directly into preg_match() without a length cap, i-regexp restriction, or bounded backtracking, allowing catastrophic-backtracking expressions to pin worker CPU and cause denial of service. This issue is fixed in versions 7.4.12 and 8.0.12.

## References
- https://github.com/symfony/symfony/releases/tag/v7.4.12
- https://github.com/symfony/symfony/releases/tag/v8.0.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45756.json
- https://github.com/symfony/symfony/security/advisories/GHSA-8v8v-g73j-492j
- https://nvd.nist.gov/vuln/detail/CVE-2026-45756
- https://github.com/symfony/symfony/commit/1ac2d47418ec23066112db1e6ca35be6fe123d14
