### Title
`computeTonConnectHash` encodes TON Connect `domain_len` as UTF-16 code-unit count instead of UTF-8 byte length, corrupting the intent hash for non-ASCII domains - (File: `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts`)

### Summary
`computeTonConnectHash` builds the domain-length field with `numberToBigEndian(domain.length, 4)` (JS UTF-16 code-unit count) but appends `new TextEncoder().encode(domain)` (UTF-8 bytes) right after it. For any `domain` containing non-ASCII characters these two numbers diverge, so the locally computed SHA-256 preimage — and therefore the resulting hash returned by `computeIntentHash` — no longer matches the canonical TON Connect `sign-data` hash that the real signer/contract computes with the correct UTF-8 byte length.

### Finding Description
The equality under test is:
`computeIntentHash(multiPayload)` (locally computed, via `computeTonConnectHash`) `==` `intent_hash` returned by `publishIntent` / computed by the intents contract, for the same `MultiPayload`.

In `computeTonConnectHash` [1](#0-0) , the domain-length prefix is built from `domain.length` (line 70) while the domain bytes themselves are `new TextEncoder().encode(domain)` (line 71). `String.prototype.length` counts UTF-16 code units, not UTF-8 bytes. Any character outside the ASCII range (accented Latin letters, CJK characters, emoji, etc.) causes `domain.length` to differ from `TextEncoder().encode(domain).length`:
- A 2-byte UTF-8 character (e.g. `é`) is 1 UTF-16 unit but 2 UTF-8 bytes.
- An astral-plane emoji (e.g. `😀`) is a UTF-16 surrogate pair (2 code units) but 4 UTF-8 bytes.

Both cases make line 70's length field wrong relative to the actual byte length written at line 71, corrupting the SHA-256 preimage described in the function's own doc comment [2](#0-1) .

This function is invoked from the standard-dispatch table `computeIntentHashHashBytes`/`computeIntentHash`, which every caller (including the `onBeforePublishIntent` hook in `IntentExecuter.signAndSendIntent`) uses to compute the hash before publishing [3](#0-2) [4](#0-3) . `MultiPayload` with `standard: "ton_connect"` is a first-class, publicly typed input to `computeIntentHash`/`signAndSendIntent` [5](#0-4) , and nothing in the JSON schema or `validate.ts` restricts `domain` to ASCII — it is declared simply as `"type": "string"` [6](#0-5) .

There is no guard (`validateAddress`, `compareAddresses`, `assert`, etc.) anywhere in this path that checks byte-length vs. code-unit-length consistency; the only existing test for this function uses ASCII domains (`"near.com"`, `"tonconnect-demo-dapp-with-wallet.vercel.app"`) so the bug is not caught [7](#0-6) [8](#0-7) .

### Impact Explanation
`onBeforePublishIntent` is documented as the mechanism integrators use to persist `intentHash` for later reconciliation with settlement [9](#0-8) , and `waitForIntentSettlement`/`getIntentStatus` are keyed by that same hash [10](#0-9) . If the locally computed hash diverges from the contract's canonical hash for a TON Connect payload with a non-ASCII `domain`, the persisted `intentHash` will never match the ticket/hash the relayer or contract actually assigns to the settled intent. The withdrawal itself is still validly signed and executes on-chain (the divergence is purely in the SDK's own local hash reproduction, not in what gets signed/submitted), but the integrator's bookkeeping — matching "intent published" to "intent settled" — breaks, stranding the record of a signed, funded withdrawal until manual reconciliation. This matches the "High: a withdrawal stuck until manual intervention" category since it is the SDK-user's own funds and requires manual intervention to reconcile status, though note it is a status/hash-tracking defect, not a fund-misrouting or double-execution defect.

### Likelihood Explanation
Preconditions: the integrator or the counterpart TON wallet must produce (or the SDK must be given) a `MultiPayload` with `standard: "ton_connect"` whose `domain` contains at least one non-ASCII character. This is entirely plausible in practice: TON Connect `domain` is typically derived from the dApp's hostname, and internationalized domain names or any accented/CJK/emoji character in the domain field will trigger the divergence — no special privilege is needed, just calling the public `computeIntentHash` (or any flow feeding through `onBeforePublishIntent`) with such a payload. It is repeatable on every call with a non-ASCII `domain`, deterministic, and requires no cost beyond constructing/receiving such a payload.

### Recommendation
Replace `domain.length` with the UTF-8 byte length, matching the bytes actually appended:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```
and reuse `domainBytes` in the `parts` array instead of re-encoding `domain` separately.

### Proof of Concept
```ts
import { describe, expect, it } from "vitest";
import { computeTonConnectHash } from "./ton-connect";
import type { MultiPayload } from "@defuse-protocol/contract-types";

describe("computeTonConnectHash domain length bug", () => {
  it("diverges from canonical UTF-8 byte-length hash for non-ASCII domain", () => {
    const payload = {
      standard: "ton_connect",
      address: "0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
      domain: "😀.example.com", // 4 UTF-16 units for emoji vs 4 UTF-8 bytes for emoji + rest ASCII
      timestamp: 1700000000,
      payload: { type: "text", text: "hello" },
      public_key: "ed25519:F8PB56zdMYNDL7Mq43DV4cV17uRqQkpn6ZygNdqavXCr",
      signature: "ed25519:not-checked-by-hash-fn",
    } satisfies Extract<MultiPayload, { standard: "ton_connect" }>;

    // Buggy hash produced by the SDK today
    const buggyHash = computeTonConnectHash(payload);

    // Canonical hash as computed with correct UTF-8 byte length for domain_len
    // (this is what the real TON Connect signer / intents contract computes,
    // simulated here to represent the mocked publishIntent's returned intent_hash)
    const canonicalHash = computeCanonicalTonConnectHash(payload);

    expect(buggyHash).not.toEqual(canonicalHash);
    // i.e. computeIntentHash(multiPayload) !== intent_hash returned by publishIntent
  });
});
```
`computeCanonicalTonConnectHash` is a small local helper duplicating `computeTonConnectHash` but using `new TextEncoder().encode(domain).length` instead of `domain.length`, representing the correct/canonical byte-length behavior a real TON Connect verifier (and thus the mocked `publishIntent` HTTP response's `intent_hash`) would produce. The test only needs to mock HTTP (`publishIntent`'s response) in a full end-to-end variant; the unit-level assertion above already demonstrates the two hashes differ for the same payload whenever `domain` contains non-ASCII characters.

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L30-49)
```typescript
/**
 * Compute the SHA-256 hash of a TON Connect payload
 *
 * For text and binary payloads:
 * Hash = SHA256(
 *   0xffff +
 *   "ton-connect/sign-data/" +
 *   workchain_id (4 bytes BE) +
 *   address (32 bytes) +
 *   domain_len (4 bytes BE) +
 *   domain +
 *   timestamp (8 bytes BE) +
 *   payload_type ("txt" or "bin") +
 *   payload_len (4 bytes BE) +
 *   payload
 * )
 *
 * @param payload - The TON Connect payload to hash
 * @returns 32-byte hash as Uint8Array
 */
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

**File:** packages/intents-sdk/src/intents/intent-hash.ts (L54-57)
```typescript
		case "ton_connect":
			return computeSignedTonConnectHash(
				signed as Extract<MultiPayload, { standard: "ton_connect" }>,
			);
```

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L88-97)
```typescript
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

**File:** packages/contract-types/src/index.ts (L1125-1142)
```typescript
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

**File:** packages/contract-types/artifacts/defuse_contract_abi.json (L4413-4416)
```json
                "domain": {
                  "description": "dApp domain",
                  "type": "string"
                },
```

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.test.ts (L10-18)
```typescript
		const payloadWithUserFriendlyAddress = {
			standard: "ton_connect",
			address: USER_FRIENDLY,
			domain: "near.com",
			timestamp: 1778685374,
			payload: { type: "text", text: "hello world" },
			public_key: "ed25519:99q8mY2bNRik43niUSKrXWsHGgmp9S6iG6VKmyta2Znj",
			signature: "ed25519:not-checked-by-hash-fn",
		} satisfies Extract<MultiPayload, { standard: "ton_connect" }>;
```

**File:** packages/intents-sdk/src/intents/intent-hash.test.ts (L70-82)
```typescript
			standard: "ton_connect",
			address:
				"0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
			domain: "tonconnect-demo-dapp-with-wallet.vercel.app",
			timestamp: 1762354640,
			payload: {
				type: "text",
				text: '{\n  "signer_id": "d1e7c122f8a43c7d7433548c4604edd4dffcfe5bb1d036499684980c115500bf",\n  "verifying_contract": "intents.near",\n  "deadline": "2035-11-03T14:57:16.445Z",\n  "nonce": "s7ne425+Pw+eVR7j02peS/wIxHKu64znkTJYeCTAfPk=",\n  "intents": []\n}',
			},
			public_key: "ed25519:F8PB56zdMYNDL7Mq43DV4cV17uRqQkpn6ZygNdqavXCr",
			signature:
				"ed25519:i5REHik6CRvvfnKsUtSDvxPeeLiPQsNMGpg9yARs9vtnZxSV9mht9K1tW2LZp8pGd4C83YZRXNG3Y5dBFdLMENd",
		},
```

**File:** packages/intents-sdk/README.md (L460-519)
```markdown
### Intent Publishing Hooks

Use the `onBeforePublishIntent` hook to intercept and process intent data before it's published to the relayer. This is
useful for persistence, logging, analytics, or custom processing:

```typescript
import {type OnBeforePublishIntentHook} from '@defuse-protocol/intents-sdk';

// Define your hook function
const onBeforePublishIntent: OnBeforePublishIntentHook = async (intentData) => {
    // Save to database for tracking
    await saveIntentToDatabase({
        hash: intentData.intentHash,
        payload: intentData.intentPayload,
        timestamp: new Date(),
    });

    // Send analytics
    analytics.track('intent_about_to_publish', {
        intentHash: intentData.intentHash,
        intentType: intentData.intentPayload.intents[0]?.intent,
    });
};

// Use the hook with the functional API
const result = await sdk.processWithdrawal({
    withdrawalParams: { /* ... */},
    intent: {
        onBeforePublishIntent, // Add the hook here
    }
});

// Or with granular control
const {intentHash} = await sdk.signAndSendWithdrawalIntent({
    withdrawalParams: { /* ... */},
    feeEstimation: fee,
    intent: {
        onBeforePublishIntent, // Add the hook here
    }
});

// Or with generic intent publishing
const {intentHash} = await sdk.signAndSendIntent({
    intents: [/* ... */],
    onBeforePublishIntent, // Add the hook here
});
```

**Hook Parameters:**

- `intentHash` - The computed hash of the intent payload
- `intentPayload` - The unsigned intent payload
- `multiPayload` - The signed multi-payload containing signature and metadata
- `relayParams` - Additional parameters passed to the relayer (quote hashes)

**Important Notes:**

- The hook is called synchronously before publishing the intent
- If the hook throws an error, the withdrawal will fail
- The hook can be async and return a Promise
```

**File:** packages/intents-sdk/README.md (L643-683)
```markdown
### Intent Management

The SDK provides direct access to intent operations for advanced use cases:

```typescript
// Generic intent signing and publishing
const {intentHash} = await sdk.signAndSendIntent({
    intents: [/* array of intent primitives */],
    signer: customIntentSigner, // optional - uses SDK default if not provided
    onBeforePublishIntent: async (data) => {
        // Custom logic before publishing
        console.log('About to publish intent:', data.intentHash);
    }
});

// Wait for intent settlement
const intentTx = await sdk.waitForIntentSettlement({
    intentHash
});

// or manual status check

// Check intent status at any time
const status = await sdk.getIntentStatus({
    intentHash: intentHash
});

console.log('Intent status:', status.status); // "PENDING" | "TX_BROADCASTED" | "SETTLED" | "NOT_FOUND_OR_NOT_VALID"

if (status.status === 'SETTLED') {
    console.log('Settlement transaction:', status.txHash);
}
```

**Intent Status Values:**

- `PENDING` - Intent published but not yet processed
- `TX_BROADCASTED` - Intent being processed, transaction broadcasted
- `SETTLED` - Intent successfully completed
- `NOT_FOUND_OR_NOT_VALID` - Intent not found or invalid, it isn't executed onchain

```
