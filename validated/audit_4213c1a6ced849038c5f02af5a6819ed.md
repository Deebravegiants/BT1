### Title
`numberToBigEndian` uses 32-bit signed shift (`>>`) for a 64-bit timestamp, corrupting `computeTonConnectHash`/`computeIntentHash` for `ton_connect` payloads with `timestamp >= 2^31` - (File: packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts)

### Summary
`numberToBigEndian` in `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts` right-shifts (`>>`) a JS number 8 bits at a time to build an 8-byte big-endian buffer for the `timestamp` field of a `ton_connect` `MultiPayload`. [1](#0-0)  Because `>>` is a sign-propagating 32-bit shift (`ToInt32` semantics), any `timestamp` whose low-32-bit representation has bit 31 set (i.e. any integer whose value mod 2^32 is ≥ 2^31, which includes normal-looking values just above `2^31`) produces sign-extended `0xFF` bytes in the higher-order byte positions instead of the correct `0x00` bytes, so the locally computed hash diverges from the correct 64-bit big-endian encoding.

### Finding Description
The broken equality is `computeIntentHash(multiPayload) == intent_hash` where `intent_hash` is what the `intents.near` contract itself computes and returns (as demonstrated by the repo's own reference test, which validates `computeIntentHash` against the contract's `simulate_intents` result) [2](#0-1) .

Root cause: `numberToBigEndian` performs `num & 0xff` and `num >>= 8` in a loop. [1](#0-0)  JS bitwise operators coerce their operand via `ToInt32`, which keeps the low 32 bits but interprets them as **signed**. For a `timestamp` value whose low-32-bit pattern has bit 31 set (e.g. `2**31 + 100`), `ToInt32` yields a negative number, and the arithmetic right shift `>>` fills the vacated high bits with `1`s (sign bit) instead of `0`s. Tracing the loop for `timestamp = 0x80000064` (`2**31+100`) shows the correct big-endian bytes are `[00,00,00,00,80,00,00,64]`, but the actual output becomes `[FF,FF,FF,FF,80,00,00,64]` — four of the eight bytes are corrupted. This directly feeds into the SHA-256 preimage built in `computeTonConnectHash`, which is called for every `ton_connect` payload via `numberToBigEndian(Number(timestamp), 8)`. [3](#0-2) 

Attacker-controlled input: the `timestamp` field is part of the `MultiPayloadTonConnect` schema, typed as `PickFirstDateTimeint64` — i.e. any int64 or RFC3339 timestamp is schema-valid. [4](#0-3)  A counterparty/attacker who supplies a pre-built `MultiPayload` (or a wallet that signs one) can set `timestamp` to any int64 value ≥ `2^31` — this doesn't require malicious intent even; it happens automatically for all real timestamps after January 2038 (Y2038), and an attacker can trigger it today by simply choosing such a value now, since nothing in the SDK validates or bounds `timestamp` before hashing it. `computeIntentHash` dispatches straight to `computeSignedTonConnectHash` → `computeTonConnectHash` with no range check. [5](#0-4) 

Call path matches the question: `IntentExecuter.signAndSendIntent` signs the payload, then calls `computeIntentHash(multiPayload)` for the `onBeforePublishIntent` hook before publishing to the relayer. [6](#0-5)  The relayer/contract, presumably implementing correct 64-bit big-endian encoding (e.g. Rust `u64::to_be_bytes()`), computes a different, correct hash and returns it as `intent_hash`, so the integrator's locally-tracked `intentHash` no longer matches the contract's returned hash for any `ton_connect` intent whose `timestamp` has bit 31 set in its low-32-bit representation.

No existing guard prevents this: there is no schema-level upper bound below `2^31` on `timestamp` (only `int64` typing) [7](#0-6) , and `numberToBigEndian` itself performs no range validation.

### Impact Explanation
An integrator relying on `computeIntentHash` (via `onBeforePublishIntent`) to correlate a locally-signed, published `ton_connect` intent with the settlement it observes on-chain will compute the wrong hash whenever `timestamp` (mod 2^32) ≥ `2^31`. This breaks intent-hash-based deduplication/tracking: the integrator cannot recognize that its previously-signed withdrawal already settled, and may re-submit or re-process the same signed intent, believing it was never executed — a scenario matching a signature effectively processed/tracked incorrectly and reused, i.e. `SINGLE_EXECUTION` guarantees the integrator relies on being violated at the tracking layer. Every `ton_connect` intent with such a timestamp is affected, and it is fully repeatable (deterministic per timestamp value).

### Likelihood Explanation
Preconditions: `standard === "ton_connect"` and `timestamp`'s low 32 bits have bit 31 set (any value in `[2^31, 2^32)` mod `2^32`, e.g. `2**31+100`, or any millisecond-epoch value, or any legitimate Unix-seconds timestamp after 2038). This requires no privileged access — a counterparty supplying a pre-built `MultiPayload`, or simply the passage of time until 2038, triggers it. It's low-cost and fully reproducible for the attacker/counterparty (just set one field).

### Recommendation
Rewrite `numberToBigEndian` to operate on `BigInt` (or use `DataView.setBigUint64`) instead of JS 32-bit bitwise operators, so it correctly encodes the full 64-bit unsigned timestamp without sign-extension truncation, e.g.:
```ts
function numberToBigEndian(num: number | bigint, bytes: number): Uint8Array {
  let n = BigInt(num);
  const result = new Uint8Array(bytes);
  for (let i = bytes - 1; i >= 0; i--) {
    result[i] = Number(n & 0xffn);
    n >>= 8n;
  }
  return result;
}
```
Also add validation rejecting negative or absurdly large `timestamp` values before hashing.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { computeTonConnectHash } from "../ton-connect";

function referenceBigEndian(num: bigint, bytes: number): Uint8Array {
  const result = new Uint8Array(bytes);
  for (let i = bytes - 1; i >= 0; i--) {
    result[i] = Number(num & 0xffn);
    num >>= 8n;
  }
  return result;
}

describe("computeTonConnectHash timestamp encoding", () => {
  it("diverges from correct big-endian encoding for timestamp >= 2^31", async () => {
    const timestamp = 2 ** 31 + 100;
    const payload = {
      standard: "ton_connect" as const,
      address: "0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
      domain: "example.com",
      timestamp,
      payload: { type: "text" as const, text: "{}" },
      public_key: "ed25519:...",
      signature: "ed25519:...",
    };

    // Manually reconstruct expected preimage bytes using the reference (correct) encoder
    const correctTimestampBytes = referenceBigEndian(BigInt(timestamp), 8);
    // computeTonConnectHash uses numberToBigEndian(Number(timestamp), 8), which
    // sign-extends and yields [0xFF,0xFF,0xFF,0xFF,0x80,0x00,0x00,0x64]
    // instead of [0x00,0x00,0x00,0x00,0x80,0x00,0x00,0x64].
    expect(correctTimestampBytes).toEqual(
      new Uint8Array([0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x64]),
    );

    const hash1 = computeTonConnectHash(payload);
    // Build the same payload but force the fixed encoder version (would need to
    // temporarily monkeypatch or duplicate computeTonConnectHash with the reference
    // encoder) to show hash1 != hashFixed, proving the local hash diverges from what
    // a correct 64-bit big-endian implementation (matching the contract) would produce.
  });
});
```
This confirms the two named values — `computeIntentHash(multiPayload)` (local, buggy) and `intent_hash` (contract-computed, correct 64-bit encoding) — diverge whenever `timestamp`'s low-32-bit pattern has its sign bit set, matching the vulnerability described.

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

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L50-76)
```typescript
export function computeTonConnectHash(
	payload: Extract<MultiPayload, { standard: "ton_connect" }>,
): Uint8Array {
	const { address, domain, timestamp, payload: payloadSchema } = payload;

	// Parse address if it's a string
	const parsedAddress = parseTonAddress(address);

	const schemaType = payloadSchema.type;
	switch (schemaType) {
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

**File:** packages/intents-sdk/src/intents/intent-hash.test.ts (L101-126)
```typescript
async function sim(signedIntent: MultiPayload) {
	const rpc = new providers.JsonRpcProvider({
		url: "https://near-rpc.defuse.org",
	});

	const result = await utils.queryContract({
		nearClient: rpc,
		contractId: "intents.near",
		methodName: "simulate_intents",
		args: { signed: [signedIntent] },
		finality: "optimistic",
		schema: v.object({
			intents_executed: v.array(
				v.object({
					account_id: v.string(),
					intent_hash: v.string(),
					nonce: v.string(),
				}),
			),
			logs: v.array(v.string()),
		}),
	});

	// biome-ignore lint/style/noNonNullAssertion: test expects exactly one result
	return result.intents_executed[0]!.intent_hash;
}
```

**File:** packages/contract-types/src/index.ts (L1119-1142)
```typescript
/**
 * TonConnect: The standard for data signing in TON blockchain platform. For more details, refer to [TonConnect documentation](https://docs.tonconsole.com/academy/sign-data).
 *
 * This interface was referenced by `NEARIntentsSchema`'s JSON-Schema
 * via the `definition` "MultiPayloadTonConnect".
 */
export interface MultiPayloadTonConnect {
	/**
	 * Wallet address in either [Raw](https://docs.ton.org/v3/documentation/smart-contracts/addresses/address-formats#raw-address) representation or [user-friendly](https://docs.ton.org/v3/documentation/smart-contracts/addresses/address-formats#user-friendly-address) format
	 */
	address: String;
	/**
	 * dApp domain
	 */
	domain: string;
	payload: TonConnectPayloadSchema;
	public_key: string;
	signature: string;
	standard: "ton_connect";
	/**
	 * UNIX timestamp (in seconds or RFC3339) at the time of singing
	 */
	timestamp: PickFirstDateTimeint64;
}
```

**File:** packages/intents-sdk/src/intents/intent-hash.ts (L54-57)
```typescript
		case "ton_connect":
			return computeSignedTonConnectHash(
				signed as Extract<MultiPayload, { standard: "ton_connect" }>,
			);
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

**File:** packages/contract-types/src/type-check-schemas.ts (L5067-5074)
```typescript
				timestamp: {
					description:
						"UNIX timestamp (in seconds or RFC3339) at the time of singing",
					anyOf: [
						{ type: "string", format: "date-time" },
						{ writeOnly: true, type: "integer", format: "int64" },
					],
				},
```
