# [H] Arbitrary local file read vulnerability during template rendering 

## Summary
Severity: High
Advisory: GHSA-2rq5-699j-x7p6
CVE: CVE-2023-25345
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-15
Source: https://github.com/advisories/GHSA-2rq5-699j-x7p6
Type: github-advisory

## Affected
- npm: `swig-templates` — affected >=0
- npm: `swig` — affected >=0

## Details
Directory traversal vulnerability in swig-templates thru 2.0.4 and swig thru 1.4.2, allows attackers to read arbitrary files via the include or extends tags.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25345
- https://github.com/node-swig/swig-templates/issues/88
