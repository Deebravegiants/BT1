# [C] Code injection in @rkesters/gnuplot

## Summary
Severity: Critical
Advisory: GHSA-f2jw-pr2c-9x96
CVE: CVE-2021-29369
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-f2jw-pr2c-9x96
Type: github-advisory

## Affected
- npm: `@rkesters/gnuplot` — affected >=0 <0.1.1

## Details
@rkesters/gnuplot is an easy to use node module to draw charts using gnuplot and ps2pdf. The gnuplot package prior to version 0.1.0 for Node.js allows code execution via shell metacharacters in Gnuplot commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29369
- https://github.com/rkesters/gnuplot/commit/23671d4d3d28570fb19a936a6328bfac742410de
- https://www.npmjs.com/package/@rkesters/gnuplot
