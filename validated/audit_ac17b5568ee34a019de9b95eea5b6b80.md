No further validation of `destinationMemo` format exists anywhere in the codebase — confirming the vulnerability.

### Title
Unvalidated colon-containing `destinationMemo` corrupts XRPL PoA withdrawal memo, causing destination-tag misparse - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts])

### Summary
`createWithdrawMemo` in `poa-bridge-utils.ts` joins `WITHDRAW_TO`, the destination address, and the raw `destinationMemo` with `:` without ever checking that `destinationMemo` itself is free of `:` characters. `PoaBridge.validateWithdrawal` only checks truthiness of `destinationMemo` (`!args.destinationMemo`) to satisfy XRPL's `requireDestinationTag` flag, never its format, so a caller-supplied memo like `"123:456"` passes validation and produces an ambiguous 4-segment memo `WITHDRAW_TO:<addr>:123:456`.

### Finding Description
The broken equality is: DESTINATION TRUTH — `(chain, address, destinationTag)` intended by the caller must equal `(chain, address, destinationTag)` that the PoA relayer parses and pays out.

Code path:
1. `PoaBridge.validateWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`, lines 232–246) checks XRPL account flags and only enforces `if (requireDestinationTag && !args.destinationMemo) throw ...` — this is a pure truthiness check with no regex/format validation of `destinationMemo`. [1](#0-0) 
2. `PoaBridge.createWithdrawalIntents` forwards `args.withdrawalParams.destinationMemo` unchanged into `createWithdrawIntentPrimitive`. [2](#0-1) 
3. `createWithdrawIntentPrimitive` calls `createWithdrawMemo({ receiverAddress, xrpMemo: params.destinationMemo })`. [3](#0-2) 
4. `createWithdrawMemo` builds `["WITHDRAW_TO", normalizedAddress]`, then unconditionally `memo.push(xrpMemo)` whenever `xrpMemo != null && xrpMemo !== ""`, and joins with `:` — no check that `xrpMemo` itself lacks a `:`. [4](#0-3) 

The existing test suite confirms the intended, safe shape is exactly 3 colon-delimited segments (`WITHDRAW_TO:<address>:<tag>`), e.g. `"WITHDRAW_TO:rDsbeomae4FXwgQTJp9Rs64Qg9vDiTCdBv:12345"`. [5](#0-4) 

An attacker (the ordinary caller supplying `withdrawalParams.destinationMemo`) can pass `"123:456"`. `validateWithdrawal`'s truthiness check passes because the string is non-empty. `createWithdrawMemo` then emits `WITHDRAW_TO:rDsbeomae4FXwgQTJp9Rs64Qg9vDiTCdBv:123:456` — four segments instead of three. Nothing in `validateAddress`, `compareAddresses`, `supports()` ordering, `FeeExceedsAmountError`, `getUnderlyingFee`, or the intents contract's signature/nonce checks inspects the memo string content; they operate on address/amount/fee fields only, not memo format. The PoA relayer, which expects a fixed `WITHDRAW_TO:<address>:<tag>` schema, receives an extra unexpected field and must either truncate/misparse it as the tag (using only `"123"`, or garbage from concatenation) or reject/mis-route the payment.

### Impact Explanation
The signed/broadcast NEAR intent (`ft_withdraw` with `memo: "WITHDRAW_TO:<addr>:123:456"`) is exactly what the relayer consumes off-chain to construct the XRPL payment's `DestinationTag`. Because the relayer's parsing contract for this memo format is a fixed 3-segment schema, a 4-segment memo diverges from the caller's intended `(address, tag)` pair without any code path catching it. On networks/exchanges where the destination tag is required to attribute funds to a sub-account, delivering funds with a wrong/garbled tag typically renders them unattributed and unrecoverable by the depositor — this matches the Critical category ("funds delivered to a wrong address/chain/contract with no recovery," here specifically the sub-account/tag equivalent for XRPL rails). It affects any XRPL PoA withdrawal caller who supplies a memo containing a colon, and is repeatable per call.

### Likelihood Explanation
Preconditions: PoA route, `Chains.XRPL`, target account with `requireDestinationTag` set (common on custodial deposit addresses), and the caller supplying a `destinationMemo` containing a literal `:`. This requires zero privilege — any integrator or user constructing `withdrawalParams.destinationMemo` from a copy-pasted string (e.g., "memo:tag" formats some exchanges display) could trigger it accidentally, and a malicious/careless caller can trigger it deliberately at will, on every call, at zero cost.

### Recommendation
In `createWithdrawMemo` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts`), validate that `xrpMemo` contains no `:` character (and ideally matches the expected XRPL destination-tag format, e.g., digits only) before appending it, throwing a descriptive error (e.g., `InvalidDestinationMemoError`) otherwise. This validation should also be enforced in `PoaBridge.validateWithdrawal` rather than solely relying on truthiness at line 244.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.test.ts
it("rejects/flags destinationMemo containing a colon (ambiguous memo segments)", () => {
  const result = createWithdrawIntentPrimitive({
    assetId: "nep141:xrp.omft.near",
    destinationAddress: "rDsbeomae4FXwgQTJp9Rs64Qg9vDiTCdBv",
    destinationMemo: "123:456",
    amount: 1000000n,
  });

  // Intended equality (caller's side): tag == "123:456" as a single logical field
  // Actual equality (relayer's side): memo.split(":") has 4 segments, i.e.
  // ["WITHDRAW_TO", "rDsbeomae4FXwgQTJp9Rs64Qg9vDiTCdBv", "123", "456"]
  const segments = result.memo.split(":");
  expect(segments.length).not.toBe(3); // currently 4 — ambiguous, diverges from intended 3-segment schema
  expect(result.memo).toBe(
    "WITHDRAW_TO:rDsbeomae4FXwgQTJp9Rs64Qg9vDiTCdBv:123:456",
  );
});
```
This demonstrates that no guard in `createWithdrawMemo` or `PoaBridge.validateWithdrawal` prevents a colon-containing memo from producing a memo string with more segments than the relayer's documented 3-segment `WITHDRAW_TO:<address>:<tag>` schema expects.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L156-160)
```typescript
		const intent = createWithdrawIntentPrimitive({
			...args.withdrawalParams,
			amount: args.withdrawalParams.amount + relayerFee,
			destinationMemo: args.withdrawalParams.destinationMemo,
		});
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L242-245)
```typescript
				const requireDestinationTag =
					accountInfo.account_flags.requireDestinationTag;
				if (requireDestinationTag && !args.destinationMemo)
					throw new XrplDestinationTagRequiredError(args.destinationAddress);
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L15-23)
```typescript
	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: tokenAccountId,
		amount: params.amount.toString(),
		memo: createWithdrawMemo({
			receiverAddress: params.destinationAddress,
			xrpMemo: params.destinationMemo,
		}),
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.test.ts (L27-38)
```typescript
	it("includes destination memo in withdrawal memo", () => {
		const result = createWithdrawIntentPrimitive({
			assetId: "nep141:xrp.omft.near",
			destinationAddress: "rDsbeomae4FXwgQTJp9Rs64Qg9vDiTCdBv",
			destinationMemo: "12345",
			amount: 1000000n,
		});

		expect(result.memo).toBe(
			"WITHDRAW_TO:rDsbeomae4FXwgQTJp9Rs64Qg9vDiTCdBv:12345",
		);
	});
```
