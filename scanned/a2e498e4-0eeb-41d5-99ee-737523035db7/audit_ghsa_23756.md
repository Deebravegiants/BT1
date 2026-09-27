# [H] Obsidian Dataview vulnerable to code injection due to unsafe eval

## Summary
Severity: High
Advisory: GHSA-xfg5-vrmc-24wc
CVE: CVE-2021-42057
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xfg5-vrmc-24wc
Type: github-advisory

## Affected
- npm: `obsidian-dataview` — affected >=0 <0.4.13

## Details
Obsidian Dataview through 0.4.12-hotfix1 allows eval injection. The `evalInContext` function in executes user input, which allows an attacker to craft malicious Markdown files that will execute arbitrary code once opened. NOTE: 0.4.13 provides a mitigation for some use cases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42057
- https://github.com/blacksmithgu/obsidian-dataview/issues/615
- https://github.com/blacksmithgu/obsidian-dataview
