# [H] High severity vulnerability that affects com.github.shyiko.ktlint:ktlint-core

## Summary
Severity: High
Advisory: GHSA-r8h9-hq9c-2p5c
CVE: CVE-2019-1010260
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-08
Source: https://github.com/advisories/GHSA-r8h9-hq9c-2p5c
Type: github-advisory

## Affected
- Maven: `com.github.shyiko.ktlint:ktlint-core` — affected >=0 <0.30.0

## Details
Using ktlint to download and execute custom rulesets can result in arbitrary code execution as the served jars can be compromised by a MITM. This attack is exploitable via Man in the Middle of the HTTP connection to the artifact servers. This vulnerability appears to have been fixed in 0.30.0 and later; after commit 5e547b287d6c260d328a2cb658dbe6b7a7ff2261.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010260
- https://github.com/shyiko/ktlint/pull/332
- https://github.com/advisories/GHSA-r8h9-hq9c-2p5c
- https://github.com/shyiko/ktlint
