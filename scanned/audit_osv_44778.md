# [H] CVE-2026-86145

## Summary
Severity: High
Advisory: CVE-2026-86145
Aliases: GHSA-3r4p-g7gg-ppmf
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86145
Type: osv

## Details
PCRE2 before 10.48 allows a pcre2_dfa_match out-of-bounds write because reuse of a cached workspace block, in a recursive DFA matching workspace, lacks a size check (even though a newly allocated block, for the same purpose, does have a size check). This outcome requires an attacker-controlled regular expression, or a recursive pattern in conjunction with a small heap limit (this can be set through the API).

## References
- http://www.openwall.com/lists/oss-security/2026/09/05/3
- https://github.com/PCRE2Project/pcre2/releases/tag/pcre2-10.48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86145.json
- https://github.com/PCRE2Project/pcre2/security/advisories/GHSA-3r4p-g7gg-ppmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-86145
