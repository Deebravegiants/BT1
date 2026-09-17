# [M] Symfony: [Yaml] Harden the parser when handling untrusted input

## Summary
Severity: Medium
Advisory: CVE-2026-45133
Aliases: GHSA-c2p3-7m5p-cv8x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-45133
Type: osv

## Details
Symfony is a PHP framework for web and console applications and a set of reusable PHP components. Prior to 5.4.52, 6.4.40, 7.4.12, and 8.0.12, when the parser is exposed to attacker-controlled input, deeply nested mappings or sequences cause both the block-level (Parser::parseBlock()) and inline (Inline::parseSequence() / Inline::parseMapping()) parsers to recurse without a depth limit. A crafted document exhausts the PHP stack and crashes the worker. This issue is fixed in versions 5.4.52, 6.4.40, 7.4.12, and 8.0.12.

## References
- https://github.com/symfony/symfony/releases/tag/v5.4.52
- https://github.com/symfony/symfony/releases/tag/v6.4.40
- https://github.com/symfony/symfony/releases/tag/v7.4.12
- https://github.com/symfony/symfony/releases/tag/v8.0.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45133.json
- https://github.com/symfony/symfony/security/advisories/GHSA-c2p3-7m5p-cv8x
- https://nvd.nist.gov/vuln/detail/CVE-2026-45133
