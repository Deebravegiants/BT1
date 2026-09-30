# [M] Regular Expression Denial of Service in jsoneditor

## Summary
Severity: Medium
Advisory: GHSA-hhfg-6hfc-rvxm
CVE: CVE-2021-3822
CWE: CWE-1333, CWE-400, CWE-697
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-hhfg-6hfc-rvxm
Type: github-advisory

## Affected
- npm: `jsoneditor` — affected >=0 <9.5.6

## Details
JSON Editor is a web-based tool to view, edit, format, and validate JSON. It has various modes such as a tree editor, a code editor, and a plain text editor. The jsoneditor package is vulnerable to ReDoS (regular expression denial of service). An attacker that is able to provide a crafted element as input to the getInnerText function may cause an application to consume an excessive amount of CPU. Below pinned line using vulnerable regex.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3822
- https://github.com/josdejong/jsoneditor/commit/092e386cf49f2a1450625617da8e0137ed067c3e
- https://github.com/josdejong/jsoneditor
- https://huntr.dev/bounties/1e3ed803-b7ed-42f1-a4ea-c4c75da9de73
