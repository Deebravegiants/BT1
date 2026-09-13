# [M] CVE-2026-89157

## Summary
Severity: Medium
Advisory: CVE-2026-89157
Aliases: GHSA-q8g2-wprr-34m9
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-89157
Type: osv

## Details
PCRE2 before 10.48, on 32-bit platforms, has a pcre2_pattern_convert out-of-bounds write when an attacker can provide a large pattern.

## References
- https://github.com/PCRE2Project/pcre2/releases/tag/pcre2-10.48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89157.json
- https://github.com/PCRE2Project/pcre2/security/advisories/GHSA-q8g2-wprr-34m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-89157
