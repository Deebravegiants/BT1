# [M] NLTK before 3.10.0 ReDoS via Text.findall() unvalidated regex

## Summary
Severity: Medium
Advisory: CVE-2026-80205
Aliases: GHSA-rrv8-h7p8-rx55, PYSEC-2026-3750
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80205
Type: osv

## Details
NLTK versions before 3.10.0 contain a regular expression denial of service vulnerability in Text.findall() and TokenSearcher.findall() methods that accept user-supplied regular expressions without validation or timeout. Attackers can supply crafted regex patterns that cause catastrophic backtracking, resulting in indefinite CPU saturation and denial of service to all users of the Python process.

## References
- http://www.openwall.com/lists/oss-security/2026/09/01/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80205.json
- https://github.com/nltk/nltk/security/advisories/GHSA-rrv8-h7p8-rx55
- https://nvd.nist.gov/vuln/detail/CVE-2026-80205
- https://www.vulncheck.com/advisories/nltk-before-3.10.0-redos-via-text-findall-unvalidated-regex
