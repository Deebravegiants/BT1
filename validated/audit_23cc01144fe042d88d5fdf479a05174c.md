### Title
`computeTonConnectHash` encodes `domain_len` using JS UTF-16 `.length` instead of UTF-8 byte length, breaking `computeIntentHash(multiPayload) == intent_hash returned by publishIntent` for non-ASCII domains - (File: packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts)

### Summary
`computeTonConnectHash` builds the TON Connect sign-data preimage using `numberToBigEndian(domain.length, 4)` (JS UTF-16 code-unit count) at line 70, while the actual domain bytes appended right after are `new TextEncoder().encode(domain)` (UTF-8 bytes) at line 71. For any `domain` string containing characters outside the ASCII/BMP-single-UTF-16-unit-but-multi-UTF-8-byte range (e.g. `á`, `ó`, emoji), the encoded length field diverges from the true UTF-8 byte length that the TON Connect spec (and any spec-compliant relayer/wallet) uses, producing a different SHA-256 hash than the one the relayer computes and returns from `publishIntent`.

### Finding Description
The broken equality is:
`computeIntentHash(multiPayload)` (locally computed in the SDK) `== intent_hash` (returned by `publishIntent`, computed by the relayer per the TON Connect spec using UTF-8 byte length).

Code path:
- `computeSignedTonConnectHash` → `computeTonConnectHash` (`packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts:50-94`) is invoked from `computeIntentHashHashBytes` (`packages/intents-sdk/src/intents/intent-hash.ts:54-57`), which is called from `computeIntentHash` (`intent-hash.ts:68-73`).
- `IntentExecuter.signAndSendIntent` calls `computeIntentHash(multiPayload)` before `onBeforePublishIntent` and before calling `this.intentRelayer.publishIntent(...)` (`packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts:90-97, 127-133`).
- Inside `computeTonConnectHash`, the `domain` field of the `ton_connect` `MultiPayload` is used twice: `numberToBigEndian(domain.length, 4)` at line 70 (JS `.length`, which counts UTF-16 code units, not bytes) and `new TextEncoder().encode(domain)` at line 71 (actual UTF-8 bytes appended to the message).

Root cause: JS string `.length` is not the UTF-8 byte length for any character requiring >1 byte in UTF-8 but only 1 UTF-16 code unit (which is the case for the entire Latin-1 Supplement, e.g. `á`, `ó`, `ñ`, and many other Unicode ranges below U+10000). Whenever `domain` contains such a character, the length prefix written to the preimage undercounts the actual byte length that follows, so the SHA-256 preimage computed by the SDK differs from a spec-correct implementation that uses `TextEncoder().encode(domain).length` for the length field, as TON Connect's spec requires.

The `domain` value originates from the `MultiPayload` supplied by the caller/wallet building the `ton_connect` signed payload (via `IntentSigner`); it is attacker/counterparty-controllable text, not something the SDK sanitizes to ASCII-only. No existing guard (`validateAddress`, `compareAddresses`, `assert` checks, etc.) validates or restricts the character set of `domain` before hashing, so the divergence is not caught anywhere in the call chain.

### Impact Explanation
This is a status/hash-misreporting bug: the SDK's locally computed `intentHash` (used in `onBeforePublishIntent` for persistence/tracking, and potentially compared against the relayer-returned hash or used to poll `waitForIntentSettlement`) will not match the actual hash the relayer computes and returns from `publishIntent` whenever the ton_connect `domain` contains any non-ASCII character whose UTF-8 encoding is longer than 1 byte but whose UTF-16 representation is 1 code unit. This matches the "High" impact category: the integrator may persist/poll the wrong hash, never observe settlement for the hash it is tracking, and potentially resubmit/double-send the intent. The condition is deterministic and repeatable on every call with such a domain — no randomness or race required.

### Likelihood Explanation
Preconditions: the caller/integrator must build a `ton_connect` `MultiPayload` whose `domain` field contains at least one character that is 1 UTF-16 code unit but >1 UTF-8 byte (extremely common for any non-English domain name, e.g. accented Latin characters, Cyrillic, etc. — IDN/punycode domains aside, this is realistic for real-world dApp domains). Attacker cost is zero — this requires no privilege, just constructing/signing a normal ton_connect payload with a legitimate international domain name. Feasibility is high and fully deterministic; it will reproduce on every affected domain string, not just adversarially crafted ones.

### Recommendation
Compute the domain length field from the UTF-8 encoded byte length, not the JS string length:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```
Reuse the already-encoded `domainBytes` for both the length prefix and the payload bytes to guarantee consistency, mirroring the existing pattern already used correctly for `payloadData` (`payloadData.length` at line 74 is already derived from the encoded bytes, not from `payloadSchema.text.length`).

### Proof of Concept
Vitest test plan (mocks HTTP only):
1. Construct a `ton_connect` `MultiPayload` with `domain = "dómain.com"` (JS `.length === 10`; UTF-8 byte length `=== 11` because `ó` encodes to 2 bytes), a fixed `address`, `timestamp`, and a text `payload`.
2. Compute `localHash = await computeIntentHash(multiPayload)` using the current SDK code.
3. Independently compute `specHash` by re-implementing the TON Connect preimage per spec: same fields, but with `numberToBigEndian(new TextEncoder().encode(domain).length, 4)` for the domain length, followed by `new TextEncoder().encode(domain)`, then `sha256(...)`, `base58.encode(...)`.
4. Mock the relayer HTTP client so `publishIntent` returns `intent_hash = specHash` (simulating a spec-compliant relayer).
5. Assert `localHash !== specHash`, demonstrating `computeIntentHash(multiPayload) !== intent_hash returned by publishIntent`.
6. As a control, assert that for an ASCII-only domain (e.g. `"domain.com"`), `localHash === specHash`, isolating the bug to non-ASCII/multi-byte-UTF-8 domains.