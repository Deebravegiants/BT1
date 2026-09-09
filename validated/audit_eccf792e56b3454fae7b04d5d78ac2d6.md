### Title
`computeTonConnectHash` diverges from the on-chain/relayer TON Connect hash for non-ASCII domains and timestamps ≥ 2^31, corrupting the intentHash persisted via `onBeforePublishIntentHook` - (File: `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts`)

### Summary
`computeTonConnectHash` in `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts` uses `domain.length` (UTF-16 code-unit count) instead of the UTF-8 byte length for `domain_len`, and `numberToBigEndian` performs `num & 0xff` / `num >>= 8` bitwise arithmetic that JavaScript coerces to 32-bit signed integers (`ToInt32`), truncating the 8-byte big-endian `timestamp` field for values ≥ 2^31. `signAndSendIntent` in `intent-executer.ts` computes `intentHash = await computeIntentHash(multiPayload)` exactly once (lines 89-97) before calling `intentRelayer.publishIntent(multiPayload)`, and passes that hash to the `onBeforePublishIntent` hook for persistence.

### Finding Description
The broken equality is: `computeIntentHash(multiPayload)` (computed locally in `intent-executer.ts:90` via `computeTonConnectHash` at `ton-connect.ts:50-94`) should equal `intent_hash` returned by `intentRelayer.publishIntent(multiPayload)` (which is derived from the same bytes by the NEAR intents contract/relayer, following the byte-length-correct TON Connect Sign Data spec).

For `standard: "ton_connect"` payloads:
- `numberToBigEndian(domain.length, 4)` at `ton-connect.ts:70` uses the JS string `.length`, which counts UTF-16 code units, not the UTF-8 encoded byte length that the spec (and presumably the on-chain verifier) requires. For a domain containing multi-byte UTF-8 characters (e.g. `日本語`), `domain.length` (code units) differs from `new TextEncoder().encode(domain).length` (UTF-8 bytes), causing a different `domain_len` field and, transitively, a completely different SHA-256 hash from what the relayer/contract computes for the identical `multiPayload` bytes.
- `numberToBigEndian` (`ton-connect.ts:13-20`) implements a big-endian byte writer using `num & 0xff` and `num >>= 8`. JavaScript's bitwise operators apply `ToInt32` to their operands, so for `timestamp` values ≥ 2^31 (e.g. `2_000_000_000_000`), `Number(timestamp)` is truncated/wrapped through 32-bit signed conversion, producing an incorrect big-endian byte sequence instead of the intended 8-byte encoding of the actual numeric value.

Both defects mean the SDK's locally-computed `intentHash`, persisted via the `OnBeforePublishIntentHook` at the single call site in `signAndSendIntent` (lines 89-97), can differ from the `intent_hash` the relayer returns for the exact same `multiPayload` object in the same call — with no additional attacker action needed beyond submitting a normal `ton_connect` withdrawal with a non-ASCII domain or large timestamp. No existing guard (`validateAddress`, `assert` checks, contract nonce/signature verification) touches this local hash computation, since it is purely a client-side convenience computation independent of the actual signature/publish path.

### Impact Explanation
This affects the `intentHash` field passed into the `OnBeforePublishIntentHook`, which integrators are documented to use "for persistence, logging, analytics, etc." (`intent-executer.ts:19-24`). If an integrator persists this value keyed to the withdrawal and later reconciles/looks up settlement status using it (e.g., via a status/hash lookup against the relayer or indexer), a mismatch means the integrator's locally-stored hash will never match the relayer-confirmed `intent_hash`, causing the integrator to believe the intent was never published/settled. This matches the "status or hash misreport making an integrator credit or refund twice" High-severity category — provided an integrator actually keys reconciliation logic off this SDK-computed `intentHash` rather than off the `Ticket`/relayer-returned value that `signAndSendIntent` and `waitForSettlement` actually use for confirmation (lines 127-135, 138-146).

Note: I was not able to fully confirm within the available context whether any first-party SDK code (e.g., `waitForIntentSettlement` or similar) itself depends on this locally-computed `intentHash` for settlement polling, as opposed to it being purely an opaque value forwarded to the optional hook for external consumers. `signAndSendIntent`'s own returned `ticket` and `waitForSettlement` use the relayer-provided ticket, not this hash, for the actual settlement wait (lines 127-146). This limits guaranteed first-party impact to the hook's persisted value being wrong, not to the SDK's own settlement flow breaking.

### Likelihood Explanation
Preconditions are narrow but deterministic and reproducible: the payload standard must be `ton_connect` (TON wallet users only), and the domain must contain non-ASCII/multi-byte UTF-8 characters, or the timestamp must exceed 2^31 (roughly year 2038, so not naturally hit today unless a wallet/app sends a millisecond-precision or otherwise oversized timestamp value). An ordinary TON Connect user with a non-English dApp domain (common for regional TON dApps) could trigger the domain-length bug without any special effort; the timestamp bug requires an unusually large timestamp, which is less likely to occur under normal wallet behavior today. The bug is 100% reproducible for any payload matching these conditions and costs the attacker/user nothing beyond normal usage.

### Recommendation
Fix `computeTonConnectHash` in `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts`:
1. Compute `domain_len` from the UTF-8 encoded byte length, not the JS string length: use `new TextEncoder().encode(domain).length` for the `numberToBigEndian` domain length argument (this is already computed as part of building `parts`, so reuse the encoded bytes' `.length` instead of `domain.length`).
2. Rewrite `numberToBigEndian` to avoid JS 32-bit bitwise coercion for the 8-byte `timestamp` field — use `BigInt` arithmetic (e.g., `DataView.setBigUint64` or manual `BigInt` shifting) so timestamps beyond 2^31 (and up to 2^53-1 safely, or full 64-bit via `BigInt`) are encoded correctly.
3. Add regression tests comparing the SDK's hash against a reference/independent TON Connect hash implementation for non-ASCII domains and large timestamps.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { computeTonConnectHash } from "../../src/intents/intent-hashes/ton-connect";
import type { MultiPayload } from "@defuse-protocol/contract-types";

function referenceTonConnectHash(payload: Extract<MultiPayload, { standard: "ton_connect" }>) {
  // Reference implementation using UTF-8 byte length for domain and BigInt-based
  // 8-byte big-endian encoding for timestamp, per TON Connect Sign Data spec.
  // ... (correct implementation)
}

describe("computeTonConnectHash divergence", () => {
  it("diverges for non-ASCII domain", () => {
    const payload = {
      standard: "ton_connect",
      address: "0:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd",
      domain: "日本語.example.com",
      timestamp: 1778685374,
      payload: { type: "text", text: "hello" },
      public_key: "ed25519:...",
      signature: "ed25519:not-checked-by-hash-fn",
    } as Extract<MultiPayload, { standard: "ton_connect" }>;

    const sdkHash = computeTonConnectHash(payload);
    const refHash = referenceTonConnectHash(payload);
    expect(sdkHash).not.toEqual(refHash); // demonstrates the divergence
  });

  it("diverges for timestamp >= 2^31", () => {
    const payload = {
      standard: "ton_connect",
      address: "0:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd",
      domain: "near.com",
      timestamp: 2_000_000_000_000,
      payload: { type: "text", text: "hello" },
      public_key: "ed25519:...",
      signature: "ed25519:not-checked-by-hash-fn",
    } as Extract<MultiPayload, { standard: "ton_connect" }>;

    const sdkHash = computeTonConnectHash(payload);
    const refHash = referenceTonConnectHash(payload);
    expect(sdkHash).not.toEqual(refHash);
  });
});
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L13-20)
```typescript
function numberToBigEndian(num: number, bytes: number): Uint8Array {
	const result = new Uint8Array(bytes);
	for (let i = bytes - 1; i >= 0; i--) {
		result[i] = num & 0xff;
		num >>= 8;
	}
	return result;
}
```

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L60-76)
```typescript
		case "text": {
			const payloadPrefix = "txt";
			const payloadData = new TextEncoder().encode(payloadSchema.text);

			// Build the message to hash
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

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L18-24)
```typescript
/**
 * Hook function called before publishing an intent.
 * Can be used for persistence, logging, analytics, etc.
 *
 * @param intentData - The intent data about to be published
 * @returns A promise that resolves when the hook is complete
 */
```

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L85-97)
```typescript
		const multiPayload = await this.intentSigner.signIntent(intentPayload);
		const relayParams = relayParamsFactory ? await relayParamsFactory() : {};

		// Call the hook before publishing if provided
		if (this.onBeforePublishIntent) {
			const intentHash = await computeIntentHash(multiPayload);
			await this.onBeforePublishIntent({
				intentHash,
				intentPayload,
				multiPayload,
				relayParams,
			});
		}
```
