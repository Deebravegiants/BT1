# [C] Deno node:crypto doesn't finalize cipher

## Summary
Severity: Critical
Advisory: GHSA-5379-f5hf-w38v
CVE: CVE-2026-22863
CWE: CWE-325
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-5379-f5hf-w38v
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.6.0

## Details
### Summary

The vulnerability allows an attacker to have infinite encryptions. 

This can lead to naive attempts at brute forcing, as well as more refined attacks with the goal to learn the server secrets.

### PoC
```js
import crypto from "node:crypto";

const key = crypto.randomBytes(32);
const iv = crypto.randomBytes(16);
const cipher = crypto.createCipheriv("aes-256-cbc", key, iv);
cipher.final()

console.log(cipher);
```

### Expected Output
```js
Cipheriv {
  _decoder: null,
  _options: undefined,
  Symbol(kHandle): CipherBase {}
}
```

### Actual Output
```js
Cipheriv {
  _events: {
    close: undefined,
    error: undefined,
    prefinish: [Function: prefinish],
    finish: undefined,
    drain: undefined,
    data: undefined,
    end: undefined,
    readable: undefined
  },
  _readableState: ReadableState {
    highWaterMark: 65536,
    buffer: [],
    bufferIndex: 0,
    length: 0,
    pipes: [],
    awaitDrainWriters: null,
    [Symbol(kState)]: 1048844
  },
  _writableState: WritableState {
    highWaterMark: 65536,
    length: 0,
    corked: 0,
    onwrite: [Function: bound onwrite],
    writelen: 0,
    bufferedIndex: 0,
    pendingcb: 0,
    [Symbol(kState)]: 17580812,
    [Symbol(kBufferedValue)]: null
  },
  allowHalfOpen: true,
  _final: [Function: final],
  _maxListeners: undefined,
  _transform: [Function: transform],
  _eventsCount: 1,
  [Symbol(kCapture)]: false,
  [Symbol(kCallback)]: null
}
```

### Mitigations

All users should upgrade to Deno v2.6.0 or newer.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-5379-f5hf-w38v
- https://nvd.nist.gov/vuln/detail/CVE-2026-22863
- https://github.com/denoland/deno
- https://github.com/denoland/deno/releases/tag/v2.6.0
