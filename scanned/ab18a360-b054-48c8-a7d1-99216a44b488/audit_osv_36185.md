# [C] OWASP CRS has multipart bypass using multiple content-type parts

## Summary
Severity: Critical
Advisory: CVE-2026-21876
Aliases: GHSA-36fv-25j3-r2c5
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-21876
Type: osv

## Details
The OWASP core rule set (CRS) is a set of generic attack detection rules for use with compatible web application firewalls. Prior to versions 4.22.0 and 3.3.8, the current rule 922110 has a bug when processing multipart requests with multiple parts. When the first rule in a chain iterates over a collection (like `MULTIPART_PART_HEADERS`), the capture variables (`TX:0`, `TX:1`) get overwritten with each iteration. Only the last captured value is available to the chained rule, which means malicious charsets in earlier parts can be missed if a later part has a legitimate charset. Versions 4.22.0 and 3.3.8 patch the issue.

## References
- https://github.com/coreruleset/coreruleset/releases/tag/v3.3.8
- https://github.com/coreruleset/coreruleset/releases/tag/v4.22.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21876.json
- https://github.com/coreruleset/coreruleset/security/advisories/GHSA-36fv-25j3-r2c5
- https://nvd.nist.gov/vuln/detail/CVE-2026-21876
- https://github.com/coreruleset/coreruleset/commit/80d80473abf71bd49bf6d3c1ab221e3c74e4eb83
- https://github.com/coreruleset/coreruleset/commit/9917985de09a6cf38b3261faf9105e909d67a7d6
- https://github.com/daytriftnewgen/CVE-2026-21876
