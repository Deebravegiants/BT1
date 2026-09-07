# [H] Joplin Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-mjr5-v9c9-mm7g
CVE: CVE-2022-40277
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-mjr5-v9c9-mm7g
Type: github-advisory

## Affected
- npm: `joplin` — affected >=0

## Details
Joplin version 2.8.8 allows an external attacker to execute arbitrary commands remotely on any client that opens a link in a malicious markdown file, via Joplin. This is possible because the application does not properly validate the schema/protocol of existing links in the markdown file before passing them to the `shell.openExternal` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40277
- https://fluidattacks.com/advisories/skrillex
- https://github.com/laurent22/joplin
