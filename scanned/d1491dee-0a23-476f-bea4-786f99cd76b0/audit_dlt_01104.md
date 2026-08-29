# [H] secp256k1-node allows private key extraction over ECDH

## Summary
Severity: High
Chain: secp256k1
Component: secp256k1, secp256k1, secp256k1
CVE: CVE-2024-48930
CWE: Exposure of Sensitive Information to an Unauthorized Actor, Improper Validation of Integrity Check Value
Published: 2024-10-21
Source: https://github.com/advisories/GHSA-584q-6j8j-r5pm
Type: github-advisory

## Details
### Summary

In `elliptic`-based version, `loadUncompressedPublicKey` has a check that the public key is on the curve: https://github.com/cryptocoinjs/secp256k1-node/blob/6d3474b81d073cc9c8cc8cfadb580c84f8df5248/lib/elliptic.js#L37-L39

`loadCompressedPublicKey` is, however, missing that check: https://github.com/cryptocoinjs/secp256k1-node/blob/6d3474b81d073cc9c8cc8cfadb580c84f8df5248/lib/elliptic.js#L17-L19

That allows the attacker to use public keys on low-cardinality curves to extract enough information to fully restore the private key from as little as 11 ECDH sessions, and very cheaply on compute power

Other operations on public keys are also affected, including e.g. `publicKeyVerify()` incorrectly returning `true` on those invalid keys, and e.g. `publicKeyTweakMul()` also returning predictable outcomes allowing to restore the tweak 

### Details

The curve equation is `Y^2 = X^3 + 7`, and it restores `Y` from `X` in `loadCompressedPublicKey`, using `Y = sqrt(X^3 + 7)`, but when there are no valid `Y` values satisfying `Y^2 = X^3 + 7` for a given `X`, the same code calculates a solution for `-Y^2 = X^3 + 7`, and that solution also satisfies some other equation `Y^2 = X^3 + D`, where `D` is not equal to 7 and might be on a curve with factorizable cardinality, so `(X,Y)` might be a low-order point on that curve, lowering the number of possible ECDH output values to bruteforcable

Those output values correspond to remainders which can be then combined with Chinese remainder theorem to restore the original value

Endomorphism-based multiplication only slightly hinders restoration and does not affect the fact that the result is low-order

10 different malicious X values could be chosen so that the overall extracted information is 238.4 bits out of 256 bit private key, and the rest is trivially bruteforcable with an additional 11th public key (which might be valid or not -- not significant)

The attacker does not need to _receive_ the ECDH value, they only need to be able to confirm it against a list of possible candidates, e.g. check if using it to decipher block/stream cipher would work -- and that could all be done locally on the attacker side

### PoC

#### Example public key

This key has order 39
One of the possible outcomes for it is a throw, 38 are predictable ECDH values
Keys used in full attack have higher order (starting from ~20000), so are very unlikely to cause an error

```js
import secp256k1 from 'secp256k1/elliptic.js'
import { randomBytes } from 'crypto'

const pub = Buffer.from('028ac57f9c6399282773c116ef21f7394890b6140aa6f25c181e9a91e2a9e3da45', 'hex')

const seen = new Set()
for (let i = 0; i < 1000; i++) {
```

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-584q-6j8j-r5pm_
