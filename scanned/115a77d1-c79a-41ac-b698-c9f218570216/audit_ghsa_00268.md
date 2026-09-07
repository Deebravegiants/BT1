# [M] markdown2 is vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-p6h9-gw49-rqm4
CVE: CVE-2018-5773
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-p6h9-gw49-rqm4
Type: github-advisory

## Affected
- PyPI: `markdown2` — affected >=0 <2.3.6

## Details
An issue was discovered in `markdown2` (aka python-markdown2) through 2.3.5. The `safe_mode` feature, which is supposed to sanitize user input against XSS, is flawed and does not escape the input properly. With a crafted payload, XSS can be triggered, as demonstrated by omitting the final `>` character from an IMG tag.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5773
- https://github.com/google/osv/issues/430
- https://github.com/trentm/python-markdown2/issues/285
- https://github.com/trentm/python-markdown2/pull/303
- https://github.com/trentm/python-markdown2/commit/1b1dcdd727c0ef03453b9f5ef5ae3679f1d72323
- https://github.com/advisories/GHSA-p6h9-gw49-rqm4
- https://github.com/pypa/advisory-database/tree/main/vulns/markdown2/PYSEC-2018-13.yaml
- https://github.com/trentm/python-markdown2
- https://github.com/trentm/python-markdown2/blob/master/CHANGES.md#python-markdown2-236
