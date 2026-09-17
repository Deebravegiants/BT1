# [H] tiny-secp256k1 vulnerable to private key extraction when signing a malicious JSON-stringifyable message in bundled environment

## Summary
Severity: High
Advisory: GHSA-7mc2-6phr-23xc
CVE: CVE-2024-49364
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-7mc2-6phr-23xc
Type: github-advisory

## Affected
- npm: `tiny-secp256k1` — affected >=0 <1.1.7

## Details
### Summary

Private key can be extracted on signing a malicious JSON-stringifiable object, when global Buffer is [`buffer` package](https://www.npmjs.com/package/buffer)

### Details

This affects only environments where `require('buffer')` is <https://npmjs.com/buffer>
E.g.: browser bundles, React Native apps, etc.

`Buffer.isBuffer` check can be bypassed, resulting in `k` reuse for different messages, leading to private key extraction over a single invalid message (and a second one for which any message/signature could be taken, e.g. previously known valid one)

v2.x is unaffected as it verifies input to be an actual `Uint8Array` instance

Such a message can be constructed for any already known message/signature pair, meaning that the attack needs only a single malicious message being signed for a full key extraction

While signing unverified attacker-controlled messages would be problematic itself (and exploitation of this needs such a scenario), signing a single message still should not leak the private key

Also, message validation could have the same bug (out of scope for this report, but could be possible in some situations), which makes this attack more likely when used in a chain

https://github.com/bitcoinjs/tiny-secp256k1/pull/140 is a subtle fix for this

### PoC

This code deliberately doesn't provide `funnyBuffer` and `extractTiny` for now, could be updated later

```js
import secp256k1 from 'tiny-secp256k1'
import crypto from 'crypto'

const key = crypto.randomBytes(32)

const msg0 = crypto.randomBytes(32)
const sig0 = secp256k1.sign(msg0, key).toString('hex')

const msg1 = funnyBuffer(msg0)
const sig1 = secp256k1.sign(msg1, key).toString('hex')

const restored = extractTiny(msg0, sig0, sig1)
console.log('Guesses:', JSON.stringify(restored, undefined, 2))
const recheck = (k) => secp256k1.sign(msg0, Buffer.from(k, 'hex')).toString('hex') === sig0
console.log('Rechecked:', JSON.stringify(restored.filter(recheck)))

console.log('Actual key', key.toString('hex'))
```

Output:
```console
Guesses: [
  "8f351953047e6b149e0595547e7d10a8a1edc61bd519b5b2514202a495e434ed",
  "ebc81e1632a1b3255589ba84364949a0a6fd0229444519765570706d394671dd"
]
Rechecked: ["ebc81e1632a1b3255589ba84364949a0a6fd0229444519765570706d394671dd"]
Actual key ebc81e1632a1b3255589ba84364949a0a6fd0229444519765570706d394671dd
```

### Impact

Full private key extraction when signing a single malicious message (that passes `JSON.stringify`/`JSON.parse` and can come from network)

## References
- https://github.com/bitcoinjs/tiny-secp256k1/security/advisories/GHSA-7mc2-6phr-23xc
- https://nvd.nist.gov/vuln/detail/CVE-2024-49364
- https://github.com/bitcoinjs/tiny-secp256k1/pull/140
- https://github.com/bitcoinjs/tiny-secp256k1
