# [M] Pathway - Unauthenticated Denial of Service via Exponential Glob Pattern Matching in Document Store

## Summary
Severity: Medium
Advisory: CVE-2026-59094
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-59094
Type: osv

## Details
Pathway through 0.31.1, fixed in commit d09722e, document store applies a caller-supplied glob pattern to indexed document paths using a hand-written recursive matcher that branches two ways on each ** token without memoization, giving exponential worst-case complexity. The filepath_globpattern value is taken from the body of the unauthenticated HTTP endpoints /v1/retrieve, /v1/inputs and /v2/answer and compiled into a filter evaluated once per indexed document, with no length or **-count limit. A remote unauthenticated attacker can submit a short pattern containing many ** tokens to consume CPU for tens of seconds per request, and a small number of requests denies service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59094.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59094
- https://www.vulncheck.com/advisories/pathway-unauthenticated-denial-of-service-via-exponential-glob-pattern-matching-in-document-store
- https://github.com/pathwaycom/pathway/pull/250
- https://github.com/pathwaycom/pathway/commit/d09722eef03fd94bba701836eb4c7fbfa3d3b88e
- https://github.com/pathwaycom/pathway
- https://github.com/pathwaycom/pathway/issues/241
