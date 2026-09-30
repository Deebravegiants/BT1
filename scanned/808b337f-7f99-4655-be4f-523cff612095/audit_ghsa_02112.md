# [H] Regular Expression Denial of Service in CairoSVG

## Summary
Severity: High
Advisory: GHSA-hq37-853p-g5cf
CVE: CVE-2021-21236
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-01-06
Source: https://github.com/advisories/GHSA-hq37-853p-g5cf
Type: github-advisory

## Affected
- PyPI: `CairoSVG` — affected >=0 <2.5.1

## Details
# Doyensec Vulnerability Advisory 

* Regular Expression Denial of Service (REDoS) in cairosvg
* Affected Product: CairoSVG v2.0.0+
* Vendor: https://github.com/Kozea
* Severity: Medium
* Vulnerability Class: Denial of Service
* Author(s): Ben Caller ([Doyensec](https://doyensec.com))

## Summary

When processing SVG files, the python package CairoSVG uses two regular expressions which are vulnerable to Regular Expression Denial of Service (REDoS).
If an attacker provides a malicious SVG, it can make cairosvg get stuck processing the file for a very long time.

## Technical description

The vulnerable regular expressions are

https://github.com/Kozea/CairoSVG/blob/9c4a982b9a021280ad90e89707eacc1d114e4ac4/cairosvg/colors.py#L190-L191

The section between 'rgb(' and the final ')' contains multiple overlapping groups.

Since all three infinitely repeating groups accept spaces, a long string of spaces causes catastrophic backtracking when it is not followed by a closing parenthesis.

The complexity is cubic, so doubling the length of the malicious string of spaces makes processing take 8 times as long.

## Reproduction steps

Create a malicious SVG of the form:

    <svg width="1" height="1"><rect fill="rgb(                     ;"/></svg>

with the following code:

    '<svg width="1" height="1"><rect fill="rgb(' + (' ' * 3456) + ';"/></svg>'

Note that there is no closing parenthesis before the semi-colon.

Run cairosvg e.g.:

    cairosvg cairo-redos.svg -o x.png

and notice that it hangs at 100% CPU. Increasing the number of spaces increases the processing time with cubic complexity.

## Remediation

Fix the regexes to avoid overlapping parts. Perhaps remove the [ \n\r\t]* groups from the regex, and use .strip() on the returned capture group.

## Disclosure timeline

- 2020-12-30: Vulnerability disclosed via email to CourtBouillon

## References
- https://github.com/Kozea/CairoSVG/security/advisories/GHSA-hq37-853p-g5cf
- https://nvd.nist.gov/vuln/detail/CVE-2021-21236
- https://github.com/Kozea/CairoSVG/commit/cfc9175e590531d90384aa88845052de53d94bf3
- https://github.com/Kozea/CairoSVG
- https://github.com/Kozea/CairoSVG/releases/tag/2.5.1
- https://github.com/pypa/advisory-database/tree/main/vulns/cairosvg/PYSEC-2021-5.yaml
- https://pypi.org/project/CairoSVG
