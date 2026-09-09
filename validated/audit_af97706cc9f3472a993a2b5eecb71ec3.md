### Title
Ambiguous same-asset withdrawal matching causes cross-reported completion status/txHash in `PoaBridge.describeWithdrawal` - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` matches a withdrawal in the POA bridge API response using only the token `assetId` via `findMatchingWithdrawal`, ignoring `destinationAddress`, `amount`, and `index`. In a batch withdrawal containing two or more withdrawals of the same `nep141:<token>` asset (e.g. `nep141:plasma.omft.near`) to different destinations, both `WithdrawalIdentifier`s resolve to the same (first-matching) array entry, so both destinations get reported the same `status`/`txHash`.

### Finding Description
The claimed equality (per-`WithdrawalIdentifier` status/txHash) is: `describeWithdrawal(wid_A).txHash == the payout that actually went to wid_A.withdrawalParams.destinationAddress` for every `wid` sharing the same NEAR intent tx. This equality is broken when a batch contains multiple withdrawals of the same `assetId`.

Root cause, traced in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`:
- `getWithdrawalStatusWithRetry` (lines 345-372) queries `poaBridge.httpClient.getWithdrawalStatus({ withdrawal_hash: args.tx.hash })` — keyed only by the shared NEAR transaction hash, which is identical for every withdrawal in the same batch/tx (`args.tx` comes from the single `intentTx` passed to `createWithdrawalIdentifiers`, see `packages/intents-sdk/src/core/withdrawal-watcher.ts` lines 80-107).
- `describeWithdrawal` (lines 313-343) calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`.
- `findMatchingWithdrawal` (lines 418-427) does `withdrawals.find((w) => \`nep141:${w.data.near_token_id}\` === assetId)` — the **first** array entry whose token matches, with no consideration of `destinationAddress`, `amount`, or the per-bridge `index` set in `createWithdrawalIdentifier` (line 295-311, which does not even store an on-chain distinguishing key, just a sequence counter).
- The function's own comment (lines 409-417) explicitly states: *"multiple withdrawals of the same token in a single transaction are not supported. POA API doesn't currently support this case either."* This is an acknowledged, unresolved gap, not a hypothetical.

Exploit flow: an integrator (or the SDK caller) builds a batch of withdrawals via `withdrawalParams: WithdrawalParams[]` where two entries share `assetId = "nep141:plasma.omft.near"` but differ in `destinationAddress` (e.g., address X and address Y). Both go into one NEAR transaction (`intentTx`). `createWithdrawalIdentifiers` assigns them `index: 0` and `index: 1` respectively, but `index` is never sent to, or used to disambiguate, the POA API response. When `waitForWithdrawalCompletion`/`watchWithdrawal` polls both identifiers, `findMatchingWithdrawal` returns the *same* first-matching withdrawal object (say, the one that actually paid address X) for **both** identifiers. The identifier for address Y therefore reports `{status: "completed", txHash: <X's tx hash>}` even though Y's actual payout (possibly still pending, failed, or to a different tx) is never inspected.

No existing guard prevents this: `supports()`, `validateAddress`, `validateWithdrawal`, and `compareAddresses` only validate a single withdrawal's own parameters (destination format, min amount, not-equal-to-token-address) — none of them cross-check against sibling withdrawals in the same batch, and none of them block or dedupe repeated `assetId` values in a batch.

### Impact Explanation
An integrator relying on `IntentsSDK.waitForWithdrawalCompletion` for a batch with duplicate `assetId` values can be told `completed` with a `txHash` for a destination that did not actually receive that payout (the misreport is attached to the wrong `WithdrawalIdentifier`). This matches the "status or hash misreport making an integrator credit or refund twice" High-severity category: an automated integrator crediting a user balance on `completed` status could credit the wrong account, or double-credit/refund if it later reconciles by tx hash and finds a mismatch. This is repeatable on every batch containing repeated `assetId` entries and is entirely attacker/caller-controlled (batch composition), requiring no privileged access — any ordinary SDK caller building the withdrawal batch triggers it.

### Likelihood Explanation
Preconditions: the caller (or an integrator forwarding user-supplied batch parameters) must submit a batch withdrawal with ≥2 entries for the same POA-routed token (`assetId`) to different destinations in a single `signAndSendWithdrawalIntent`/`processWithdrawal` call, then rely on `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` for status. Nothing in `supports()`, `validateWithdrawal()`, or the batch-building code (`createWithdrawalIdentifiers`) rejects or warns about duplicate `assetId` in a batch, so this is trivially reachable and low-cost (one transaction, standard SDK usage). The bug is deterministic once the POA API returns ≥2 entries for the shared `withdrawal_hash`.

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId`: use `destinationAddress` (and `destinationMemo`/amount where applicable) in addition to token id, or — as the code comment itself suggests — sort both the API's returned withdrawals and the local `withdrawalParams` by `amount` (since relayer fees are equal per token) and match by position/index instead of doing an unconditional `.find()`. At minimum, when more than one withdrawal entry matches the same `assetId` for a given `tx.hash`, `describeWithdrawal` should refuse to resolve (return `pending` or throw) rather than silently returning the first match, and the SDK should either reject batches with duplicate `assetId` values or clearly document/guard against this until the POA API supports disambiguation.

### Proof of Concept
```ts
// vitest, mocking only HTTP (poaBridge.httpClient.getWithdrawalStatus)
import { describe, it, expect, vi } from "vitest";
import { PoaBridge } from "../poa-bridge";
import { poaBridge } from "@defuse-protocol/internal-utils";

describe("PoaBridge.describeWithdrawal same-asset batch ambiguity", () => {
  it("misattributes status/txHash across two withdrawals of the same assetId", async () => {
    const sameHash = { hash: "near-tx-shared", accountId: "user.near" };
    const assetId = "nep141:plasma.omft.near";

    // API returns two entries for the single shared tx hash: one COMPLETED to X, one PENDING to Y
    vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
      withdrawals: [
        {
          status: "COMPLETED",
          data: { near_token_id: "plasma.omft.near", transfer_tx_hash: "0xHASH_FOR_X" /* ... */ },
        },
        {
          status: "PENDING",
          data: { near_token_id: "plasma.omft.near", transfer_tx_hash: null /* ... */ },
        },
      ],
    } as any);

    const bridge = new PoaBridge({ envConfig: /* ... */, xrplRpcUrls: [] });

    const widX = { landingChain: /* ... */, index: 0, withdrawalParams: { assetId, amount: 1n, destinationAddress: "X", feeInclusive: true }, tx: sameHash };
    const widY = { landingChain: /* ... */, index: 1, withdrawalParams: { assetId, amount: 1n, destinationAddress: "Y", feeInclusive: true }, tx: sameHash };

    const statusX = await bridge.describeWithdrawal(widX);
    const statusY = await bridge.describeWithdrawal(widY);

    // BROKEN EQUALITY: widY (destination Y, actually still pending) is reported as "completed"
    // with X's txHash, identical to widX's result, instead of "pending".
    expect(statusX).toEqual({ status: "completed", txHash: "0xHASH_FOR_X" });
    expect(statusY).toEqual({ status: "completed", txHash: "0xHASH_FOR_X" }); // demonstrates the bug: should be {status:"pending"}
  });
});
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-343)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const response = await this.getWithdrawalStatusWithRetry(args);

		// Response list is unsorted, so we match by assetId instead of index
		const withdrawal = findMatchingWithdrawal(
			response.withdrawals,
			args.withdrawalParams.assetId,
		);

		if (withdrawal == null) {
			return { status: "pending" };
		}

		if (withdrawal.status === "PENDING") {
			return { status: "pending" };
		}

		if (withdrawal.status === "COMPLETED") {
			return {
				status: "completed",
				txHash: withdrawal.data.transfer_tx_hash,
			};
		}

		return {
			status: "failed",
			reason: withdrawal.status,
		};
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L345-372)
```typescript
	private async getWithdrawalStatusWithRetry(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatusResponse> {
		const startTime = Date.now();

		while (true) {
			try {
				return await poaBridge.httpClient.getWithdrawalStatus(
					{ withdrawal_hash: args.tx.hash },
					{
						baseURL: this.getPoaBridgeBaseURL(),
						logger: args.logger,
					},
				);
			} catch (err: unknown) {
				if (!isWithdrawalNotFoundError(err)) {
					throw err;
				}

				if (Date.now() - startTime >= NOT_FOUND_RETRY_TIMEOUT_MS) {
					return { withdrawals: [] };
				}

				args.logger?.warn("Withdrawal not indexed yet, retrying...");
				await sleep(NOT_FOUND_RETRY_INTERVAL_MS);
			}
		}
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-427)
```typescript
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	// POA bridge only supports NEP-141 tokens. The API returns `near_token_id`
	// (e.g., "zec.omft.near") which we prefix with "nep141:" to match assetId format.
	// Note: `defuse_asset_identifier` cannot be used as it contains chain-native
	// format (e.g., "zec:mainnet:native") which differs from the assetId format.
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L80-107)
```typescript
export async function createWithdrawalIdentifiers(args: {
	bridges: Bridge[];
	withdrawalParams: WithdrawalParams[];
	intentTx: NearTxInfo;
}): Promise<{ bridge: Bridge; wid: WithdrawalIdentifier }[]> {
	const indexes = new Map<string, number>();
	const results: { bridge: Bridge; wid: WithdrawalIdentifier }[] = [];

	for (const w of args.withdrawalParams) {
		const bridge = await findBridgeForWithdrawal(args.bridges, w);
		if (bridge == null) {
			throw new BridgeNotFoundError();
		}

		const currentIndex = indexes.get(bridge.route) ?? 0;
		indexes.set(bridge.route, currentIndex + 1);

		const wid = bridge.createWithdrawalIdentifier({
			withdrawalParams: w,
			index: currentIndex,
			tx: args.intentTx,
		});

		results.push({ bridge, wid });
	}

	return results;
}
```

**File:** packages/intents-sdk/src/shared-types.ts (L434-441)
```typescript
export interface WithdrawalIdentifier {
	/** Actual chain where funds arrive; Near for virtual/internal routes */
	landingChain: Chain;
	/** Per-bridge withdrawal sequence number */
	index: number;
	withdrawalParams: WithdrawalParams;
	tx: NearTxInfo;
}
```
