# [M] NLTK 3.10.2 Regular Expression Denial of Service via tgrep

## Summary
Severity: Medium
Advisory: CVE-2026-80206
Aliases: GHSA-w3v8-gmh9-3wv7, PYSEC-2026-3751
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80206
Type: osv

## Details
NLTK before 3.10.3 contains a regular expression denial of service (ReDoS) vulnerability in the tgrep module. The _tgrep_node_action function compiles user-supplied regular expressions embedded in /regex/ pattern nodes and executes them via re.search against tree node labels without any validation or timeout. An attacker who controls the tgrep pattern (e.g., via tgrep_positions() or tgrep_compile() exposed to external input) can supply a pattern that triggers catastrophic backtracking, causing indefinite CPU saturation that blocks the Python process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80206.json
- https://github.com/nltk/nltk/security/advisories/GHSA-w3v8-gmh9-3wv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-80206
- https://www.vulncheck.com/advisories/nltk-3.10.2-regular-expression-denial-of-service-via-tgrep
