# [M] python-multipart affected by Denial of Service via large multipart preamble or epilogue data

## Summary
Severity: Medium
Advisory: GHSA-mj87-hwqh-73pj
CVE: CVE-2026-40347
CWE: CWE-400, CWE-834
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-mj87-hwqh-73pj
Type: github-advisory

## Affected
- PyPI: `python-multipart` — affected >=0 <0.0.26

## Details
### Summary

A denial of service vulnerability exists when parsing crafted `multipart/form-data` requests with large preamble or epilogue sections.

### Details

Two inefficient multipart parsing paths could be abused with attacker-controlled input.

Before the first multipart boundary, the parser handled leading CR and LF bytes inefficiently while searching for the start of the first part. After the closing boundary, the parser continued processing trailing epilogue data instead of discarding it immediately. As a result, parsing time could grow with the size of crafted data placed before the first boundary or after the closing boundary.

### Impact

An attacker can send oversized malformed multipart bodies that consume excessive CPU time during request parsing, reducing request-handling capacity and delaying legitimate requests. This issue degrades availability but does not typically result in a complete denial of service for the entire application.

### Mitigation

Upgrade to version `0.0.26` or later, which skips ahead to the next boundary candidate when processing leading CR/LF data and immediately discards epilogue data after the closing boundary.

## References
- https://github.com/Kludex/python-multipart/security/advisories/GHSA-mj87-hwqh-73pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-40347
- https://github.com/Kludex/python-multipart
- https://github.com/Kludex/python-multipart/releases/tag/0.0.26
