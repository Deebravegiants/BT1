# [C] goose 1.37.0 Arbitrary Command Execution via Recipe Extensions

## Summary
Severity: Critical
Advisory: CVE-2026-85623
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85623
Type: osv

## Details
goose 1.37.0 executes arbitrary commands from recipe stdio extensions and retry.checks without security inspection. Attackers can distribute malicious recipes that execute shell commands as the user running goose, bypassing the recipe security scan which does not inspect extensions or retry configurations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85623.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85623
- https://www.vulncheck.com/advisories/goose-1.37.0-arbitrary-command-execution-via-recipe-extensions
- https://github.com/aaif-goose/goose/issues/10325
- https://github.com/aaif-goose/goose
- https://github.com/aaif-goose/goose/blob/v1.49.0/crates/goose/src/agents/extension_manager.rs
- https://github.com/aaif-goose/goose/blob/v1.49.0/crates/goose/src/recipe/mod.rs
