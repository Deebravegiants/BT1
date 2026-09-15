# [C] stoqey/gnuplot is vulnerable to command injection

## Summary
Severity: Critical
Advisory: GHSA-795w-7426-m94j
CVE: CVE-2021-33360
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-795w-7426-m94j
Type: github-advisory

## Affected
- npm: `@stoqey/gnuplot` — affected >=0

## Details
An issue found in Stoqey gnuplot v.0.0.3 and earlier allows attackers to execute arbitrary code via the src/index.ts, plotCallack, child_process, and/or filePath parameter(s).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33360
- https://advisory.checkmarx.net/advisory/CX-2021-4811
- https://github.com/stoqey/gnuplot
- https://github.com/stoqey/gnuplot/blob/cd76060a15f58348baeef1c5fd867ce856515949/src/index.ts#L211-L217
