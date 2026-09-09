### Title
Non-ASCII TON Connect `domain` causes `computeTonConnectHash` to use UTF-16 code-unit length instead of UTF-8 byte length, breaking local/contract hash equality - (File: packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts)

### Summary
`computeTonConnectHash` prefixes the domain bytes with `numberToBigEndian(domain.length, 4)`, where `domain.length` is the JS string's UTF-16 code-unit count, not the UTF-8 byte length of `new TextEncoder().encode(domain)`. For any non-ASCII domain (e.g. containing `é`), the length prefix diverges from the number of bytes actually appended and from the length the TON wallet used when it signed the payload per the TON Connect sign-data spec, producing a locally computed hash that does not equal the actual signed/verified intent hash.

### Finding Description
The broken equality is:
`computeIntentHash(multiPayload)` (client, via `computeTonConnectHash` in `packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts:70-71`) **should equal** `intent_hash` returned by `publishIntent` (`packages/internal-utils/src/solverRelay/publishIntent.ts:29-33`), which reflects the hash actually verified against the wallet-produced signature (built using the TON Connect spec's byte-length-based `domain_len`).

Root cause: [1](#0-0)  uses `domain.length` (UTF-16 code units) as the 4-byte big-endian `domain_len` field, while the actual domain bytes appended are `new TextEncoder().encode(domain)` (UTF-8 bytes). For ASCII domains these two counts coincide, but for any domain containing multi-byte UTF-8 characters (e.g. `"café.example"`) `domain.length` (code units) is smaller than the true UTF-8 byte count, so the length prefix and the appended byte content are internally inconsistent, and this reconstruction diverges from whatever byte sequence the TON wallet actually hashed and signed (which uses the real byte length per the TON Connect `sign-data` documentation referenced in the file's own docstring at lines 30-45).

Exploit flow: `IntentExecuter.signAndSendIntent` calls `computeIntentHash(multiPayload)` in the `onBeforePublishIntent` hook (`packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts:90-96`) before calling `this.intentRelayer.publishIntent(...)` (line 127). If an integrator persists `intentHash` from this hook to later poll/settle the intent, and the ton_connect payload's `domain` contains non-ASCII characters, the persisted hash will not match the `intent_hash` returned by the relayer/contract for the same signed payload.

Existing guards do not catch this: there is no runtime assertion comparing the locally computed hash against the relayer's returned hash anywhere in `intent-executer.ts`, and the only existing test for `computeTonConnectHash` (`ton-connect.test.ts`) uses the ASCII domain `"near.com"`, so the non-ASCII length bug is untested and unguarded.

### Impact Explanation
The hash mismatch means whatever hash an integrator persists via `onBeforePublishIntent` for a ton_connect-signed withdrawal will not correspond to the real on-chain/relayer intent hash. Any downstream logic (e.g. `waitForSettlement`/status polling, or integrator bookkeeping keyed by hash) using the locally computed hash will poll or reference the wrong identifier, leaving a legitimate withdrawal appearing unsettled indefinitely from the integrator's perspective — matching the "withdrawal stuck until manual intervention" / "status misreport" High-impact category. It does not itself let an attacker redirect funds, but it can cause integrators or users to believe a settled withdrawal never completed, prompting a retry/double-send of the underlying instruction against their own funds.

### Likelihood Explanation
This triggers whenever a `ton_connect` MultiPayload's `domain` field contains any character requiring more than one UTF-8 byte per UTF-16 code unit (any non-ASCII character, not limited to surrogate pairs). No special privilege is needed — any caller constructing/signing a ton_connect payload with a non-ASCII domain string (e.g. an internationalized dApp domain, or a domain string with unicode content forwarded by a counterparty) hits it deterministically and repeatably every time; it is not a probabilistic race, it is a pure encoding bug.

### Recommendation
Replace `domain.length` with the actual UTF-8 byte length in `computeTonConnectHash`:
```ts
const domainBytes = new TextEncoder().encode(domain);
...
numberToBigEndian(domainBytes.length, 4),
domainBytes,
```
and reuse `domainBytes` for both the length prefix and the appended data, ensuring the value is consistent with what the TON wallet computed during signing.

### Proof of Concept
Vitest test in `packages/intents-sdk/src/intents/intent-hashes/ton-connect.test.ts`:
```ts
it("domain_len must reflect UTF-8 byte length, not UTF-16 code units", () => {
  const domain = "café.example"; // 12 UTF-16 code units, 13 UTF-8 bytes
  const payload = {
    standard: "ton_connect",
    address: "0:fa63f5195b0f8682d3f3413e2b40decfae7778b3691748a2d55dae5b243a3054",
    domain,
    timestamp: 1762354640,
    payload: { type: "text", text: "hello" },
    public_key: "ed25519:...",
    signature: "ed25519:not-checked-by-hash-fn",
  } satisfies Extract<MultiPayload, { standard: "ton_connect" }>;

  const actualDomainBytes = new TextEncoder().encode(domain).length; // 13
  const usedLength = domain.length; // 12

  expect(usedLength).not.toEqual(actualDomainBytes);

  // Recompute hash with the correct (spec-compliant) UTF-8 byte length prefix
  // and assert it differs from computeTonConnectHash(payload), proving
  // computeIntentHash(multiPayload) !== the hash the wallet actually signed
  // (and thus !== intent_hash returned by publishIntent for the same payload).
  const wrongHash = computeTonConnectHash(payload);
  const correctHash = computeTonConnectHashWithByteLength(payload); // reference impl using domainBytes.length
  expect(wrongHash).not.toEqual(correctHash);
});
```
This isolates and proves the divergence purely from the length-computation bug, matching the equality violation described. [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts (L50-94)
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

			// Concatenate all parts
			const totalLength = parts.reduce((sum, part) => sum + part.length, 0);
			const message = new Uint8Array(totalLength);
			let offset = 0;
			for (const part of parts) {
				message.set(part, offset);
				offset += part.length;
			}

			return sha256(message);
		}
		default: {
			schemaType satisfies never;
			throw new Error(`Unknown TON Connect payload type: ${schemaType}`);
		}
	}
}
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

**File:** packages/internal-utils/src/solverRelay/publishIntent.ts (L16-34)
```typescript
export function publishIntent(
	signatureData: WalletSignatureResult,
	userInfo: { userAddress: string; userChainType: AuthMethod },
	quoteHashes: string[],
	config: solverRelay.httpClient.RequestConfig = {},
): Promise<Result<PublishIntentReturnType, PublishIntentErrorType>> {
	return publishIntents(
		{
			signed_datas: [prepareSwapSignedData(signatureData, userInfo)],
			quote_hashes: quoteHashes,
		},
		config,
	).then((result) => {
		return result.map((intentHashes) => {
			const intentHash = intentHashes[0];
			assert(intentHash != null, "Should include at least one intent hash");
			return intentHash;
		});
	});
```

**File:** packages/intents-sdk/src/intents/intent-hashes/ton-connect.test.ts (L1-29)
```typescript
import { describe, expect, it } from "vitest";
import type { MultiPayload } from "@defuse-protocol/contract-types";
import { computeTonConnectHash } from "./ton-connect";

describe("computeTonConnectHash", () => {
	it("produces identical hash whether the address is raw or user-friendly", () => {
		const USER_FRIENDLY = "UQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_YiM";
		const RAW =
			"0:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd";
		const payloadWithUserFriendlyAddress = {
			standard: "ton_connect",
			address: USER_FRIENDLY,
			domain: "near.com",
			timestamp: 1778685374,
			payload: { type: "text", text: "hello world" },
			public_key: "ed25519:99q8mY2bNRik43niUSKrXWsHGgmp9S6iG6VKmyta2Znj",
			signature: "ed25519:not-checked-by-hash-fn",
		} satisfies Extract<MultiPayload, { standard: "ton_connect" }>;

		const payloadWithRawAddress = {
			...payloadWithUserFriendlyAddress,
			address: RAW,
		} satisfies Extract<MultiPayload, { standard: "ton_connect" }>;

		expect(computeTonConnectHash(payloadWithUserFriendlyAddress)).toEqual(
			computeTonConnectHash(payloadWithRawAddress),
		);
	});
});
```
