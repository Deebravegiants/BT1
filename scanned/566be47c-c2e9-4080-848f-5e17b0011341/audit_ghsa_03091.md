# [H] Prototype pollution in json8-merge-patch

## Summary
Severity: High
Advisory: GHSA-8v9x-9xqg-r8mr
CVE: CVE-2020-8268
CWE: CWE-1321, CWE-20, CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-8v9x-9xqg-r8mr
Type: github-advisory

## Affected
- npm: `json8-merge-patch` — affected >=0 <1.0.3

## Details
Prototype pollution vulnerability in json8-merge-patch npm package < 1.0.3 may allow attackers to inject or modify methods and properties of the global object constructor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8268
- https://github.com/sonnyp/JSON8/issues/113
- https://github.com/sonnyp/JSON8/commit/2e890261b66cbc54ae01d0c79c71b0fd18379e7e#diff-faa7bef039022bc7ca1c613331b2373950ddd3d65ebf25d1699fbdf89773a387
- https://hackerone.com/reports/980649
- https://www.npmjs.com/package/json8-merge-patch
