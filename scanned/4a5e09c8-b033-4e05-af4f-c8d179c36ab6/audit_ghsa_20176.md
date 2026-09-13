# [H] OS Command Injection in proctree

## Summary
Severity: High
Advisory: GHSA-cv76-rv4h-4mqc
CVE: CVE-2021-34082
CWE: CWE-78
Ecosystem: npm
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-cv76-rv4h-4mqc
Type: github-advisory

## Affected
- npm: `proctree` — affected >=0

## Details
OS Command Injection vulnerability in allenhwkim proctree through 0.1.1 and commit 0ac10ae575459457838f14e21d5996f2fa5c7593 for Node.js, allows attackers to execute arbitrary commands via the fix function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34082
- https://advisory.checkmarx.net/advisory/CX-2021-4783
- https://github.com/allenhwkim/proctree
- https://github.com/allenhwkim/proctree/blob/master/index.js#L46
