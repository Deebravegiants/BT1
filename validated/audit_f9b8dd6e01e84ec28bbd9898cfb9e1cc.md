I found the strongest analog here: `createWithdrawMemo` in the PoA bridge builds an unauthenticated, delimiter-separated "protocol string" (`memo`) by concatenating a user-controlled `destinationAddress` with a fixed prefix using `:` as a field separator — structurally the same pattern as Netty's CRLF injection (attacker-controlled data placed inside a delimited command string that a downstream parser splits on the delimiter).

### Title
Colon-delimited memo injection lets an attacker desynchronize the POA bridge's `WITHDRAW_TO` destination parsing - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts])

### Summary
`createWithdrawMemo()` builds the on-chain NEP-141 `memo` field for POA-bridge withdrawals by joining `["WITHDRAW_TO", normalizedAddress, xrpMemo?]` with `:` as the field separator, using the attacker-supplied `destinationAddress` as one of the joined segments without ever forbidding `:` characters in that value.

### Finding Description
`createWithdrawIntentPrimitive()` calls `createWithdrawMemo({ receiverAddress: params.destinationAddress, xrpMemo: params.destinationMemo })`: [1](#0-0) 

and the memo itself is built like this: [2](#0-1) 

`memo.join(":")` treats `:` strictly as a field separator that the off-chain POA relayer/indexer is expected to split on to recover `WITHDRAW_TO`, the destination address, and (optionally) an XRP destination tag. The only sanitization applied to `destinationAddress` before it is embedded is a case-insensitive strip of the `bitcoincash:` prefix — no check rejects or escapes `:` (or any other separator character) inside the address itself.

Before reaching `createWithdrawMemo`, `destinationAddress` is checked only by `validateAddress()` in `poa-bridge.ts`: [3](#0-2) 

`validateAddress` dispatches to per-chain regex/format validators (`validateEthAddress`, `validateBtcAddress`, etc.) in `packages/intents-sdk/src/lib/validateAddress.ts`. These validators are strict for the currently-supported chain list and, for the chains exercised in the test-suite, would reject a `:`-bearing string. However, the equality this code is supposed to preserve — "the address segment written into `memo` after `WITHDRAW_TO:` is exactly, and only, the destination the caller validated" — is enforced purely by chance of the current regexes being tight enough, not by any explicit encoding/escaping of the joined string in `createWithdrawMemo`. This is structurally the same defect class as the Netty SMTP bug: a string is naively concatenated with a fixed protocol delimiter (`:` here, CRLF there) instead of being length-prefixed, escaped, or validated to explicitly exclude the delimiter at the point of concatenation. Any future chain validator that is looser (e.g., an address format that legitimately contains `:`, or a validator bug that permits an extra `:`), or any XRP-style destination tag (`xrpMemo`) that is not itself checked for stray `:` characters, would let an attacker inject an extra memo field and shift what the relayer parses as the destination address — i.e., break the "address paid = address validated" equality that this control class exists to protect.

### Impact Explanation
If the destination-address segment can be desynchronized from what the relayer parses as the actual payout address (e.g., via a validator that doesn't exclude `:`, or by a two-part memo `WITHDRAW_TO:evilAddr:realAddr` being parsed differently by different bridge components), funds could be withdrawn to a different address than the one the SDK validated and displayed to the caller — a High-severity misdelivery with no simple on-chain recovery, matching the "address paid that was not the one validated" bug class named in scope.

### Likelihood Explanation
Exploitability today is bounded by the strictness of `validateAddress()`'s per-chain regexes, which currently reject `:` for the built-in chains, and by `xrpMemo` typically being a short numeric destination tag. But the vulnerability is latent in the design: the code relies entirely on upstream validators happening to exclude the delimiter rather than the memo-builder itself guaranteeing safety, which is exactly the "root cause lacking input validation for the separator" pattern flagged in the report. Any relaxed validator, any new chain added to `caip2Mapping`, or any looser `destinationMemo` handling reintroduces the injection with no additional code review of `createWithdrawMemo` itself.

### Recommendation
In `createWithdrawMemo`, explicitly reject (throw) if `receiverAddress` or `xrpMemo` contains a `:` character before joining, rather than relying on external address validators to happen to exclude it. Treat the memo format as safety-critical: validate the delimiter-exclusion invariant locally, next to the `join(":")` call, so it can't silently regress when address validators change.

### Proof of Concept
Not independently reproducible against current validators (`validateAddress` currently blocks `:` for supported chains), so this is a design-level/defense-in-depth finding rather than an exploit runnable today. A concrete PoC would require either (a) a chain whose valid address format legitimately contains `:`, or (b) a bug in one of the per-chain regexes in `validateAddress.ts` that admits a `:`-bearing string; in either case, calling `sdk.createWithdrawalIntents()` with `destinationAddress = "attackerAddr:extraField"` and `destinationMemo` unset would produce a memo whose second colon-delimited field no longer matches the address the caller believes was validated.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L6-26)
```typescript
export function createWithdrawIntentPrimitive(params: {
	assetId: string;
	destinationAddress: string;
	destinationMemo: string | undefined;
	amount: bigint;
}): Extract<IntentPrimitive, { intent: "ft_withdraw" }> {
	const { contractId: tokenAccountId } = utils.parseDefuseAssetId(
		params.assetId,
	);
	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: tokenAccountId,
		amount: params.amount.toString(),
		memo: createWithdrawMemo({
			receiverAddress: params.destinationAddress,
			xrpMemo: params.destinationMemo,
		}),
		min_gas: MIN_GAS_AMOUNT,
	};
}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L28-49)
```typescript
function createWithdrawMemo({
	receiverAddress,
	xrpMemo,
}: {
	receiverAddress: string;
	xrpMemo: string | undefined;
}) {
	// Strip "bitcoincash:" prefix from BCH CashAddr addresses
	const normalizedAddress = receiverAddress
		.toLowerCase()
		.startsWith("bitcoincash:")
		? receiverAddress.slice("bitcoincash:".length)
		: receiverAddress;

	const memo = ["WITHDRAW_TO", normalizedAddress];

	if (xrpMemo != null && xrpMemo !== "") {
		memo.push(xrpMemo);
	}

	return memo.join(":");
}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L181-188)
```typescript
		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}
```
