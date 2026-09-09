Confirmed: no code path in this repo decodes an X-address into its embedded classic address + tag, and nothing rejects the combination of an X-address `destinationAddress` with a non-empty `destinationMemo`.

### Title
XRPL X-address + destinationMemo produces a memo string with two conflicting destination tags - (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts`)

### Summary
`validateXrpAddress` accepts XRPL X-addresses (which embed their own destination tag) via `xrp_isValidXAddress`, and `createWithdrawMemo` concatenates the raw `destinationAddress` string with the separately supplied `xrpMemo`/`destinationMemo` without ever decoding the X-address or checking for a tag collision. This lets an attacker submit an X-address encoding tag `N` together with a `destinationMemo` encoding tag `M`, producing a single memo string that embeds two different tag values.

### Finding Description
The equality that must hold is: for a given withdrawal, the effective `(chain, address, tag)` triple paid to the recipient must be single-valued — i.e., the tag encoded in the address (if any) and the tag supplied via `destinationMemo` must not both exist and disagree.

- `validateAddress` for `Chains.XRPL` calls `validateXrpAddress`, which accepts either a classic address OR an X-address: [1](#0-0) 
- Nothing in `validateXrpAddress`, `PoaBridge.validateWithdrawal`, or `createWithdrawIntentPrimitive` decodes the X-address to extract its embedded tag or checks it against `destinationMemo`: [2](#0-1) 
- `createWithdrawMemo` takes the raw `receiverAddress` string (which could be an X-address) and appends `xrpMemo` verbatim, joined by `:`: [3](#0-2) 

Attacker input: `destinationAddress` = a valid XRPL X-address encoding tag `N` (passes `xrp_isValidXAddress`), `destinationMemo` = `"M"` where `M != N`. This passes `validateAddress` (format check only) and `validateWithdrawal` (which only checks `requireDestinationTag && !destinationMemo`, satisfied since memo is non-empty) with no rejection anywhere in the traced path. The resulting memo is `"WITHDRAW_TO:<xaddr-encoding-N>:M"` — a string carrying two distinct, unreconciled tag values.

Existing guards do not catch this: `validateAddress` only validates format, not semantic consistency; `compareAddresses` and `DestinationAddressMatchesTokenAddressError` check for self-transfers, not tag collisions; the XRPL-specific checks in `validateWithdrawal` only look at `requireDestinationTag` vs. presence of `destinationMemo`, never decoding the X-address itself.

### Impact Explanation
This is a genuine SDK-side defect: the SDK itself constructs and signs a `ft_withdraw` intent whose `memo` field is internally inconsistent (self-contradictory as to the intended destination tag), rather than normalizing/rejecting the ambiguous input. Whether this actually causes a misroute at the receiving exchange depends entirely on how the external, off-repo PoA bridge/relayer parses `"WITHDRAW_TO:<addr>:<memo>"` — specifically whether it (a) rejects X-addresses in this field, (b) decodes the X-address and ignores/overrides the appended memo, or (c) blindly treats everything after the first `:` as a literal tag and uses that, discarding the X-address's embedded tag. That interpretation logic lives in the PoA bridge / off-chain indexer, which per the rules is out of scope ("defects inside intents.near, bridge contracts, or third-party SDKs with no path through this repo"). The repo-local root cause (accepting X-addresses in `validateAddress` and not decoding/reconciling them against `destinationMemo` in `createWithdrawMemo`) is real, but the concrete "funds credited under wrong tag" outcome cannot be attributed to this repo's code without asserting behavior of the external bridge component.

### Likelihood Explanation
Trivial to trigger for any caller — supply an X-address plus any memo value; no privileged access, RPC state, or timing is needed.

### Recommendation
In `createWithdrawMemo`/`validateWithdrawal`, when the blockchain is XRPL: reject (or decode) X-addresses. If `destinationAddress` is an X-address, decode it to its classic address + embedded tag internally, and throw if a separate non-empty `destinationMemo` is also supplied and disagrees with (or simply coexists with) the embedded tag — enforcing a single source of truth for the tag before building the `WITHDRAW_TO` memo.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.test.ts
it("does NOT reject conflicting X-address tag + destinationMemo (currently)", () => {
  const xAddress = "X7AcgcsBL6XDcUb289X4mJ8djcdyKaB5hJDWMArnXr61cqZ"; // encodes tag N, e.g. 1
  const result = createWithdrawIntentPrimitive({
    assetId: "nep141:xrp.omft.near",
    destinationAddress: xAddress,
    destinationMemo: "999999", // tag M, disagrees with N
    amount: 1000000n,
  });

  // Both tag encodings end up concatenated with no reconciliation:
  expect(result.memo).toBe(`WITHDRAW_TO:${xAddress}:999999`);
  // No exception thrown despite the address already embedding a (different) tag.
});
```
This demonstrates the SDK-local defect (unreconciled dual-tag memo construction). Establishing the "funds lost" impact additionally requires confirming, outside this repo, how the PoA bridge parses this exact memo format for X-address inputs — which is out of scope for this audit.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L333-335)
```typescript
function validateXrpAddress(address: string) {
	return xrp_isValidClassicAddress(address) || xrp_isValidXAddress(address);
}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L170-220)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
		skipMinAmountValidation?: boolean;
		destinationMemo?: string;
	}): Promise<void> {
		const assetInfo = this.parseAssetId(args.assetId);
		assert(assetInfo != null, "Asset is not supported");

		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}

		// Use cached getSupportedTokens to avoid frequent API calls
		const { tokens } = await this.getCachedSupportedTokens(
			[toPoaNetwork(assetInfo.blockchain)],
			args.logger,
		);

		const tokenInfo = tokens.find(
			(token) => token.intents_token_id === args.assetId,
		);

		if (tokenInfo == null) {
			throw new UnsupportedAssetIdError(
				args.assetId,
				"`assetId` is not supported in PoA bridge.",
			);
		}

		if (
			tokenInfo.origin_chain_address !== "native" &&
			compareAddresses(
				tokenInfo.origin_chain_address,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenInfo.origin_chain_address,
				args.assetId,
			);
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
