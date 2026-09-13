# [M] sqlparse: formatting list of tuples leads to denial of service

## Summary
Severity: Medium
Advisory: GHSA-27jp-wm6q-gp25
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-27jp-wm6q-gp25
Type: github-advisory

## Affected
- PyPI: `sqlparse` — affected >=0 <0.5.4

## Details
### Summary
The below gist hangs while attempting to format a long list of tuples.

This was found while [drafting a regression test for Dja
ngo 5.2's composite primary key feature](https://code.djangoproject.com/ticket/36416#comment:3), which allows querying composite fields with tuples.

###

## References
- https://github.com/andialbrecht/sqlparse/security/advisories/GHSA-27jp-wm6q-gp25
- https://github.com/andialbrecht/sqlparse/commit/40ed3aa958657fa4a82055927fa9de70ab903360
- https://github.com/andialbrecht/sqlparse
- https://github.com/andialbrecht/sqlparse/releases/tag/0.5.4
