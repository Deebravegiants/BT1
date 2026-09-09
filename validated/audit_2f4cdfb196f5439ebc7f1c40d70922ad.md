### Title
`FEE_SUBSIDIZED_TOKENS` is keyed by `assetId` only, not by `(assetId, destinationChain)`, letting a subsidized-token withdrawal to an unintended chain zero out a genuine relayer fee - ([File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts])

### Summary
`OmniBridge.estimateWithdrawalFee` unconditionally forces `fee.native_token_fee = 0n` whenever `withdrawalParams.assetId` is present in `FEE_SUBSIDIZED_TOKENS`, without checking the destination chain the withdrawal is actually routed to. Because `routeConfig.chain` lets a caller pick a destination chain independent of the token's default origin chain, a subsidized asset routed to a chain the subsidy was never meant to cover still has its real, non-zero `native_token_fee` zeroed, and `validateWithdrawal`'s relayer-fee sanity check is also skipped for the same reason.

### Finding Description
The broken equality is: `underlyingFees.relayerFee` should equal the true relayer cost returned by `BridgeAPI.getFee` for the specific `(assetId, destinationChain)` route, but the code makes it equal `0n` for *any* destination chain as long as `assetId` matches `FEE_SUBSIDIZED_TOKENS`: [1](#0-0) 

`FEE_SUBSIDIZED_TOKENS` is a flat list of asset IDs with no chain dimension: [2](#0-1) 

The destination chain used to call `getFee` is derived from `makeAssetInfo`, which honors an attacker-controlled `routeConfig.chain` when present, independent of the token's own origin chain: [3](#0-2) 

The SDK's own test suite confirms that a token can legitimately be withdrawn to a chain other than its natural origin chain via `routeConfig`, e.g. `nep141:token.publicailab.near` withdrawn with `routeConfig` pointed at Solana: [4](#0-3) 

`estimateWithdrawalFee` then calls `getFee` with the chain derived from `assetInfo.blockchain` (which reflects the attacker-supplied `routeConfig.chain`), gets back a genuine, non-zero `native_token_fee` for that route, and immediately zeroes it purely based on the `assetId` match: [5](#0-4) 

`validateWithdrawal` compounds this: the assertion that would normally guarantee a non-UTXO-chain withdrawal has `relayerFee > 0n` is skipped entirely whenever `isFeeSubsidized` is true, again without checking the chain: [6](#0-5) [7](#0-6) 

No other guard (`validateAddress`, `compareAddresses`, `supports()` ordering, `getUnderlyingFee`, `FeeExceedsAmountError`) reintroduces a chain check on the subsidy decision; they validate address formats and fee-vs-amount relations, not whether the subsidy is scoped to the correct chain.

### Impact Explanation
`feeEstimation.amount`/`underlyingFees.relayerFee` end up as `0n` (plus quote/storage fees) even though the Omni relayer genuinely incurs `native_token_fee` cost for bridging on the unintended chain; this amount is never charged to the withdrawing user via the token_diff intent built in `createWithdrawalIntents`. The relayer/protocol absorbs the real cost with nothing recovered from the user — an uncharged real cost, repeatable on every call to `estimateWithdrawalFee`/withdrawal for the subsidized `assetId` combined with an off-target `routeConfig.chain`.

### Likelihood Explanation
Exploitability depends on: (1) the token in `FEE_SUBSIDIZED_TOKENS` genuinely supporting withdrawal to more than one destination chain (i.e., it has a bridged deployment/token address on a chain other than the one the subsidy was intended for, verified via `getCachedDestinationTokenAddress`/`getBridgedToken`), and (2) `getFee` returning a non-zero `native_token_fee` for that other chain. If the specific token currently in the constant only ever resolves to a single destination chain, this is not exploitable today, but the code contains no structural check preventing it from becoming exploitable the moment a second chain is supported for that asset, or if additional assets are added to `FEE_SUBSIDIZED_TOKENS` that support multiple chains. Cost to the attacker is a single SDK call with `routeConfig.chain` set to the unintended chain.

### Recommendation
Change `FEE_SUBSIDIZED_TOKENS` (and the `isFeeSubsidized` checks in both `estimateWithdrawalFee` and `validateWithdrawal`) to be keyed by `(assetId, destinationChain)` pairs rather than `assetId` alone, and only zero the fee / skip the relayer-fee assertion when both the asset and the resolved destination chain match the intended subsidized route.

### Proof of Concept
```ts
// vitest, mocking only BridgeAPI.getFee (HTTP boundary)
it("zeroes real relayer fee for a subsidized asset routed to an unintended chain", async () => {
  const bridge = new OmniBridge({ envConfig: configsByEnvironment.production, nearProvider });

  vi.spyOn(bridge["omniBridgeAPI"], "getFee").mockResolvedValue({
    native_token_fee: 12345n, // genuine, non-zero relayer cost on this route
    gas_fee: null,
    protocol_fee: null,
    min_amount: null,
    insufficient_utxo: false,
  });

  const withdrawalParams = {
    assetId: "nep141:lsd-usdt.rhealab.near", // in FEE_SUBSIDIZED_TOKENS
    destinationAddress: "<valid address on unintended chain>",
    routeConfig: createOmniBridgeRoute(Chains.Solana), // chain the subsidy was NOT configured for
    amount: 1_000_000n,
  };

  const feeEstimation = await bridge.estimateWithdrawalFee({ withdrawalParams });

  // Broken equality: relayerFee should equal the real 12345n cost, but is forced to 0n
  expect(feeEstimation.underlyingFees[RouteEnum.OmniBridge].relayerFee).toBe(0n); // actual (buggy) behavior
  // Correct behavior would require:
  // expect(feeEstimation.underlyingFees[RouteEnum.OmniBridge].relayerFee).toBe(12345n);
  expect(feeEstimation.amount).not.toContain(12345n); // 12345 never charged to the user
});
```

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L259-281)
```typescript
	makeAssetInfo(assetId: string, routeConfig?: RouteConfig) {
		const parsed = parseDefuseAssetId(assetId);
		if (parsed.standard !== "nep141") return null;
		let omniChainKind: ChainKind | null = null;
		let blockchain: Chain | null = null;
		if (this.targetChainSpecified(routeConfig)) {
			omniChainKind = caip2ToChainKind(routeConfig.chain);
			blockchain = routeConfig.chain;
		} else {
			omniChainKind = this.isPoaTokenMigratedToOmniBridge(parsed.contractId)
				? poaContractIdToChainKind(parsed.contractId)
				: parseOriginChain(parsed.contractId);
			if (omniChainKind === null) return null;
			blockchain = chainKindToCaip2(omniChainKind);
		}
		if (omniChainKind === null || blockchain === null) return null;

		return Object.assign(parsed, {
			blockchain,
			bridgeName: BridgeNameEnum.Omni,
			address: parsed.contractId,
		});
	}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L341-349)
```typescript
		const isFeeSubsidized = FEE_SUBSIDIZED_TOKENS.includes(args.assetId);
		const isPrefundedWithdrawal =
			this.bridgeConfig.prefundedNativeFeeTokens.includes(args.assetId);
		if (!isFeeSubsidized && !isPrefundedWithdrawal) {
			assert(
				args.feeEstimation.amount > 0n,
				`Invalid Omni Bridge fee: expected > 0, got ${args.feeEstimation.amount}`,
			);
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L440-455)
```typescript
		if (!utxoChainWithdrawal && !isFeeSubsidized) {
			const relayerFee = getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.OmniBridge,
				"relayerFee",
			);
			// Currently only UTXO chains withdrawals can have 0 relayerFee
			assert(
				getUnderlyingFee(
					args.feeEstimation,
					RouteEnum.OmniBridge,
					"relayerFee",
				) > 0n,
				`Invalid Omni Bridge relayer fee for non UTXO chain withdrawal: expected > 0, got ${relayerFee}`,
			);
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L559-588)
```typescript
		const fee = await withTimeout(
			() =>
				this.omniBridgeAPI.getFee(
					omniAddress(ChainKind.Near, this.envConfig.contractID),
					omniAddress(omniChainKind, args.withdrawalParams.destinationAddress),
					omniAddress(ChainKind.Near, assetInfo.contractId),
					args.withdrawalParams.amount,
				),
			{
				timeout: typeof window !== "undefined" ? 10_000 : 3000,
				errorInstance: new OmniWithdrawalApiFeeRequestTimeoutError(),
			},
		);
		// Native token fee can be zero for BTC withdrawals
		if (fee.native_token_fee === null || fee.native_token_fee < 0n) {
			throw new InvalidFeeValueError(
				args.withdrawalParams.assetId,
				fee.native_token_fee,
			);
		}

		// Omni API returns non-zero fee for subsidized tokens, so we enforce 0 fee for specific tokens.
		if (FEE_SUBSIDIZED_TOKENS.includes(args.withdrawalParams.assetId)) {
			fee.native_token_fee = 0n;
		}

		const underlyingFees: RouteFeeStructures[RouteEnum["OmniBridge"]] = {
			relayerFee: fee.native_token_fee,
			storageDepositFee: 0n,
		};
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge-constants.ts (L12-13)
```typescript
// API returns non-zero fee for them; however, these tokens have own relayers that bridge them for free.
export const FEE_SUBSIDIZED_TOKENS = ["nep141:lsd-usdt.rhealab.near"];
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts (L101-106)
```typescript
				const assetId = "nep141:token.publicailab.near";
				const routeConfig = createOmniBridgeRoute(Chains.Solana);

				await expect(bridge.supports({ assetId, routeConfig })).resolves.toBe(
					true,
				);
```
