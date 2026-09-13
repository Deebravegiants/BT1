# [M] GuardDog: Unsanitized human-readable scan output allows terminal escape injection from malicious package content

## Summary
Severity: Medium
Advisory: CVE-2026-44972
Aliases: GHSA-m5p4-gvpx-4mvr, PYSEC-2026-2506
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44972
Type: osv

## Details
GuardDog is a CLI tool to identify malicious PyPI packages. From 2.6.0 to 2.9.0, GuardDog includes attacker-controlled filenames, file locations, messages, and code snippets in its default human-readable output without escaping terminal control characters. A malicious package can therefore inject ANSI or OSC escape sequences into analyst terminals or CI logs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44972.json
- https://github.com/DataDog/guarddog/security/advisories/GHSA-m5p4-gvpx-4mvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44972
