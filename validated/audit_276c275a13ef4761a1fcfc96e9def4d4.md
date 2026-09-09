This is exactly the ground-truth check the question asks for — `sim()` in `packages/intents-sdk/src/intents/intent-hash.test.ts:101-126` calls the real `intents.near` contract's `simulate_intents` method to get the authoritative `intent_hash`, and the existing test suite already compares `computeIntentHash(multiPayload)` against it for every standard, including `ton_connect` — but only with ASCII domains (`"tonconnect-demo-dapp-with-wallet.vercel.app"`, `"near.com"`). No existing test exercises a non-ASCII domain, so the divergence is untested.

### Title
`computeTonConnectHash` uses UTF-16 code-unit length instead of UTF-8 byte length for `domain_len`, causing local/on-chain hash divergence for non-ASCII domains - (File: `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts`)

### Summary
`computeTonConnectHash` builds the TON Connect sign-data preimage using `domain.length` (JS `String.length`, i.e. UTF-16 code units) as the 4-byte big-endian `domain_len` prefix, but appends `new TextEncoder().encode(domain)` (UTF-8 bytes) as the actual domain bytes. For any `domain` containing non-ASCII characters these two counts diverge, producing a self-inconsistent, incorrect SHA-256 preimage and thus a wrong hash whenever `computeIntentHash` is called on a `ton_connect` `MultiPayload` with such a domain.

### Finding Description
The broken equality is:
`computeIntentHash(multiPayload)` (client-computed) == `intent_hash` returned by the `intents.near` contract for the identical `multiPayload` (ground truth, verified in-repo by `sim()` via `simulate_intents`).

Code path:
- `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts:50-88` (`computeTonConnectHash`) builds: [1](#0-0) 
  Line 70 uses `domain.length` (JS string length = UTF-16 code units) for the length prefix, while line 71 appends the actual UTF-8-encoded bytes of `domain`. For ASCII-only domains these are numerically equal (1 code unit = 1 byte), so no divergence is observed — this is why the existing tests (`ton-connect.test.ts`, and the `ton_connect` case in `intent-hash.test.ts`) all pass: every domain used (`"near.com"`, `"tonconnect-demo-dapp-with-wallet.vercel.app"`) is pure ASCII.
- For a domain containing any character encoded to >1 byte in UTF-8 (e.g. `"café.com"`, or a Cyrillic homoglyph domain such as `"аpple.com"` using U+0430), `domain.length` (8 for `"café.com"`) diverges from `new TextEncoder().encode(domain).length` (9, because `é` is 2 UTF-8 bytes). The resulting hash preimage carries a length prefix that does not match the number of domain bytes that actually follow it — an internally inconsistent message relative to the TON Connect sign-data format documented directly above the function (`domain_len (4 bytes BE) + domain`), where `domain_len` is defined as the byte length of `domain`.
- This function is called by `computeSignedTonConnectHash` → `computeIntentHashHashBytes` → `computeIntentHash` (`packages/intents-sdk/src/intents/intent-hash.ts:54-57,68-73`), which is invoked by `IntentExecuter.signAndSendIntent` at `packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts:90` — *before* `publishIntent` is called at line 127 — exactly the ordering the question describes: the locally-computed hash is captured and handed to `onBeforePublishIntent` prior to publishing, so any divergence is baked into whatever the integrator persists.
- Existing guards (`validateAddress`, `parseTonAddress`, `supports()` ordering, etc.) do nothing to protect the `domain_len` computation; none of them touch this length-prefix logic.

### Impact Explanation
The `intentHash` value delivered to an integrator's `onBeforePublishIntent` hook (and any hash the integrator persists from `computeIntentHash`) can differ from the actual `intent_hash` the `intents.near` contract computes and returns/emits for the identical signed `multiPayload`, for any TON Connect intent whose `domain` contains non-ASCII characters. If an integrator uses the locally computed hash as the key to track settlement (matching it against `waitForIntentSettlement`/relay-reported hashes), the persisted record will never match the on-chain event for that intent. This is a status/hash misreport that can cause the integrator to treat a successfully published and settled intent as unmatched/failed, risking a duplicate re-publish or a double credit/refund on the same signed funds movement — matching the High severity category "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Preconditions: the TON Connect signer must be used, and the `domain` echoed by the wallet in `TonConnectSignatureData.domain` (flowing through `prepareSwapSignedData` in `packages/internal-utils/src/utils/prepareBroadcastRequest.ts:57-67`) must contain at least one character outside the ASCII range. TonConnect domains are dApp-supplied/wallet-echoed strings and are not restricted to ASCII by anything in this SDK — an ordinary user connecting through their own wallet/dApp session with an internationalized (IDN) or homoglyph domain triggers it at zero cost, deterministically, on every call. This is fully repeatable for as long as the integrator uses a non-ASCII-domain TonConnect flow.

### Recommendation
In `computeTonConnectHash` (`packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts`), compute the domain bytes once and use their byte length for the prefix:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```
instead of `numberToBigEndian(domain.length, 4)` / re-encoding `domain` separately. Add a regression test with a non-ASCII domain compared against `simulate_intents` ground truth (same pattern as `sim()` in `intent-hash.test.ts`).

### Proof of Concept
Vitest test plan (mocks HTTP only, per rule):
1. Build a `ton_connect` `MultiPayload` with `domain: "café.com"` (or a Cyrillic homoglyph domain) and a fixed `address`, `timestamp`, `payload.text`.
2. Mock `intentRelayer.publishIntent` (relay HTTP client) to resolve with a hardcoded ticket/hash representing the "on-chain" `intent_hash` for that exact payload (obtainable ahead of time from `simulate_intents`, as `sim()` already does for other cases).
3. Call `IntentExecuter.signAndSendIntent(...)` with an `onBeforePublishIntent` hook capturing `intentHash`.
4. Assert `computeIntentHash(multiPayload)` (captured hash) equals the mocked/on-chain `intent_hash`.
5. Show the assertion fails today because `domain.length` (8) !== `new TextEncoder().encode(domain).length` (9) for `"café.com"`, causing a different SHA-256 preimage/hash than the byte-length-correct computation the contract performs.
6. After applying the fix (using `domainBytes.length`), the assertion passes.

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L65-76)
```typescript
			const parts: Uint8Array[] = [
				new Uint8Array([0xff, 0xff]),
				new TextEncoder().encode("ton-connect/sign-data/"),
				numberToBigEndian(parsedAddress.workchainId, 4),
				parsedAddress.address,
				numberToBigEndian(domain.length, 4),
				new TextEncoder().encode(domain),
				numberToBigEndian(Number(timestamp), 8),
				new TextEncoder().encode(payloadPrefix),
				numberToBigEndian(payloadData.length, 4),
				payloadData,
			];
```
