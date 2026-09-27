# [H] Uncontrolled resource consumption in braces

## Summary
Severity: High
Advisory: GHSA-grv7-fg5c-xmjg
CVE: CVE-2024-4068
CWE: CWE-1050, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-grv7-fg5c-xmjg
Type: github-advisory

## Affected
- npm: `braces` — affected >=0 <3.0.3

## Details
The NPM package `braces` fails to limit the number of characters it can handle, which could lead to Memory Exhaustion. In `lib/parse.js,` if a malicious user sends "imbalanced braces" as input, the parsing will enter a loop, which will cause the program to start allocating heap memory without freeing it at any moment of the loop. Eventually, the JavaScript heap limit is reached, and the program will crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4068
- https://github.com/micromatch/braces/issues/35
- https://github.com/micromatch/braces/pull/37
- https://github.com/micromatch/braces/pull/40
- https://github.com/micromatch/braces/commit/415d660c3002d1ab7e63dbf490c9851da80596ff
- https://devhub.checkmarx.com/cve-details/CVE-2024-4068
- https://github.com/micromatch/braces
- https://github.com/micromatch/braces/blob/98414f9f1fabe021736e26836d8306d5de747e0d/lib/parse.js#L308
