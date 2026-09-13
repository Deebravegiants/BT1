# [M] justhtml before 1.18.0 Denial of Service via CSS Selector

## Summary
Severity: Medium
Advisory: CVE-2026-4671
Aliases: GHSA-r8cj-3554-33mr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-23
Source: https://osv.dev/vulnerability/CVE-2026-4671
Type: osv

## Details
justhtml before 1.18.0 contains multiple low-severity denial-of-service issues in CSS selector handling and linkification. Applications that evaluate attacker-controlled selector strings (via query(), matches(), or selector-based transforms), run selector matching over very large untrusted documents, construct DOM trees from untrusted structure, or enable linkification over attacker-controlled text may consume disproportionate CPU or memory. Triggers include oversized selectors, large selector lists, oversized compound selectors, long combinator chains, deeply nested functional pseudo-classes, repeated token/positional matching, cyclic DOM graphs causing non-terminating traversal, and punctuation-heavy or trailing-bracket linkification input. These are availability-only concerns and do not by themselves allow script execution, data disclosure, or sanitizer bypass. Default JustHTML(sanitize=True) usage is not expected to be exposed, since selectors are normally supplied by application code.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4671.json
- https://github.com/EmilStenstrom/justhtml/security/advisories/GHSA-r8cj-3554-33mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-4671
- https://www.vulncheck.com/advisories/justhtml-before-denial-of-service-via-css-selector
