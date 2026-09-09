### Title
UTXO withdrawal signs an understated `MaxGasFee` from a stale/attacker-supplied `feeEstimation` without re-validating against a fresh Omni Bridge fee - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts)

### Summary
`deriveOmniWithdrawIntentParams`'s UTXO branch reads `utxoMaxGasFee`/`utxoProtocolFee` from the caller-supplied `feeEstimation` and writes them verbatim into `amount` and the signed `msg.MaxGasFee`, without cross-checking them against a fresh `omniBridgeAPI.getFee` response. `OmniBridge.validateWithdrawal` does call `omniBridgeAPI.getFee` for UTXO chains, but only uses the fresh result to check `insufficient_utxo` and the minimum-amount threshold — it never compares the fresh fee cost to the caller's `utxoMaxGasFee`/`utxoProtocolFee`. A caller that passes a stale (lower) `feeEstimation` therefore gets a signed `ft_withdraw` whose `amount` and `msg.MaxGasFee` are both understated relative to the real current UTXO relayer/connector cost.

### Finding Description
The broken equality: `signed msg.MaxGasFee` (and the fee portion of `amount`) should equal the **current** UTXO connector cost obtained from a fresh `omniBridgeAPI.getFee` call at withdrawal time. Instead:

- `deriveOmniWithdrawIntentParams` builds `amount += utxoMaxGasFee + utxoProtocolFee` and `msg = JSON.stringify({ MaxGasFee: utxoMaxGasFee.toString() })` purely from `getUnderlyingFee(params.feeEstimation, RouteEnum.OmniBridge, "utxoMaxGasFee"/"utxoProtocolFee")`, with only a `> 0n` sanity assert, never a freshness check. [1](#0-0) 

- `OmniBridge.validateWithdrawal` does fetch a fresh fee via `this.omniBridgeAPI.getFee(...)` for UTXO chains, but the resulting `fee` object is only used for `insufficient_utxo` and `fee.min_amount`; the caller-supplied `utxoMaxGasFee`/`utxoProtocolFee` from `feeEstimation` are used as-is to compute `actualAmountWithFee` for the minimum-amount check — they are never compared against a live gas-fee/protocol-fee figure from the fresh response. [2](#0-1) 

- `OmniBridge.createWithdrawalIntents` and the top-level `IntentsSDK.createWithdrawalIntents` simply forward the same `args.feeEstimation` object into `deriveOmniWithdrawIntentParams` after `validateWithdrawal` returns — there is no second fee fetch or recomputation between validation and intent construction. [3](#0-2) [4](#0-3) 

Attacker's exact input: a `feeEstimation.underlyingFees[RouteEnum.OmniBridge]` object with `utxoMaxGasFee`/`utxoProtocolFee` set below the bridge's current fee (e.g., obtained from an earlier quote and replayed), while `amount` is still large enough to clear the freshly-fetched `min_amount` threshold. Because `validateWithdrawal`'s only guard tied to the live fee call is the `min_amount` comparison — not a fee-value equality check — this passes validation, then `deriveOmniWithdrawIntentParams` signs `ft_withdraw` with the understated `amount` and `msg.MaxGasFee`.

None of the listed guards intercept this: `assert(utxoMaxGasFee > 0n)` only rejects zero/negative values, not stale-but-positive ones; `validateAddress`/`compareAddresses` are address checks unrelated to fee freshness; `FeeExceedsAmountError` is not raised on this path; `getUnderlyingFee` simply reads whatever the caller put in `feeEstimation` without validating provenance; `matchesRequest` is not part of this bridge's flow as shown.

### Impact Explanation
The signed `ft_withdraw.msg.MaxGasFee` and `amount` end up lower than the real current UTXO connector cost. Since the relayer picking up the withdrawal transaction is constrained to at most `MaxGasFee` (per the code's own comment about preventing a malicious relayer from charging more), an understated value means the relayer cannot cover the real connector fee, and the withdrawal will not be able to complete as signed — it stalls until manual intervention (re-quoting, resubmission, or support involvement). This matches the "High — withdrawal stuck until manual intervention" category. The affected party is the withdrawing user's own transaction (or, if forwarded by an integrator using a stale quote, that integrator's end user); it is repeatable on every withdrawal for which a stale/low `feeEstimation` object is supplied.

### Likelihood Explanation
Preconditions: the destination chain must be BTC or Zcash (`isUtxoChain`), and the caller must supply a `feeEstimation` object whose `utxoMaxGasFee`/`utxoProtocolFee` are below the bridge's live cost yet still large enough that `amount + utxoMaxGasFee + utxoProtocolFee >= fee.min_amount`. This is easy to arrange: a caller holding an earlier, since-expired quote (fees generally trend in one direction with network congestion) can replay it, or an integrator that caches fee estimates can pass a stale one. No special privilege is required — this uses only the public `createWithdrawalIntents`/`validateWithdrawal` surface with attacker-controlled `feeEstimation` content. It is repeatable per withdrawal attempt.

### Recommendation
In `OmniBridge.validateWithdrawal` (and/or `deriveOmniWithdrawIntentParams`), compare the caller-supplied `utxoMaxGasFee`/`utxoProtocolFee` against the values derived from the fresh `omniBridgeAPI.getFee` response for the same withdrawal, and reject (or re-derive) when the supplied fee is lower than the current bridge-quoted fee, rather than checking only `min_amount`/`insufficient_utxo`. Alternatively, have `createWithdrawalIntents` recompute UTXO fees from a fresh quote instead of trusting the caller-supplied `feeEstimation` for these specific fields.

### Proof of Concept
Vitest plan (mocks HTTP only, via `BridgeAPI.prototype.getFee`):
1. Mock `BridgeAPI.prototype.getFee` to return a fresh fee response with a high, current gas cost (e.g. implied `utxoMaxGasFee` of `1000n`) and `min_amount: "1500"`, `insufficient_utxo: false`.
2. Call `bridge.validateWithdrawal({ assetId: "nep141:btc.bridge.near", amount: 3000n, destinationAddress: "bc1q...", feeEstimation: { amount: 1100n, quote: null, underlyingFees: { [RouteEnum.OmniBridge]: { utxoMaxGasFee: 100n /* stale, real cost is ~1000n */, utxoProtocolFee: 50n, relayerFee: 0n, storageDepositFee: 0n } } } })` — assert it **resolves** (passes) because `3000n + 100n + 50n >= 1500n`.
3. Call `deriveOmniWithdrawIntentParams({ assetId: "nep141:btc.bridge.near", destinationAddress: "bc1q...", actualAmount: 3000n, omniChainKind: ChainKind.Btc, intentsContract: "intents.near", feeEstimation: <same stale feeEstimation> })`.
4. Assert `JSON.parse(result.msg)` equals `{ MaxGasFee: "100" }` — i.e., the stale, understated value — rather than the fresh `1000n` value the mocked `getFee` implied, demonstrating `signed msg.MaxGasFee (100n) != real current UTXO connector cost (1000n)`.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts (L92-116)
```typescript
	if (isUtxoChain(params.omniChainKind)) {
		const utxoMaxGasFee = getUnderlyingFee(
			params.feeEstimation,
			RouteEnum.OmniBridge,
			"utxoMaxGasFee",
		);
		const utxoProtocolFee = getUnderlyingFee(
			params.feeEstimation,
			RouteEnum.OmniBridge,
			"utxoProtocolFee",
		);
		assert(
			utxoMaxGasFee !== undefined && utxoMaxGasFee > 0n,
			`Invalid Omni Bridge utxo max gas fee: expected > 0, got ${utxoMaxGasFee}`,
		);
		assert(
			utxoProtocolFee !== undefined && utxoProtocolFee > 0n,
			`Invalid Omni Bridge utxo protocol fee: expected > 0, got ${utxoProtocolFee}`,
		);

		// UTXO withdrawals add protocol + max gas fees to the intent amount since they're paid
		// from the withdrawn asset, not wrap.near.
		amount += utxoMaxGasFee + utxoProtocolFee;
		msg = JSON.stringify({ MaxGasFee: utxoMaxGasFee.toString() });
	}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L304-327)
```typescript
		if (args.feeEstimation.quote !== null) {
			intents.push({
				intent: "token_diff",
				diff: {
					[args.feeEstimation.quote.defuse_asset_identifier_in]:
						`-${args.feeEstimation.quote.amount_in}`,
					[args.feeEstimation.quote.defuse_asset_identifier_out]:
						args.feeEstimation.quote.amount_out,
				},
				referral: args.referral,
			});
		}
		intents.push(
			...createWithdrawIntentsPrimitive(
				deriveOmniWithdrawIntentParams({
					assetId: args.withdrawalParams.assetId,
					destinationAddress: args.withdrawalParams.destinationAddress,
					actualAmount: args.withdrawalParams.amount,
					omniChainKind,
					intentsContract: this.envConfig.contractID,
					feeEstimation: args.feeEstimation,
				}),
			),
		);
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L457-519)
```typescript
		if (utxoChainWithdrawal) {
			// UTXO availability and minimum withdrawal thresholds for UTXO chains are sourced
			// from the Omni Bridge indexer.
			const fee = await withTimeout(
				() =>
					this.omniBridgeAPI.getFee(
						omniAddress(ChainKind.Near, this.envConfig.contractID),
						omniAddress(omniChainKind, args.destinationAddress),
						omniAddress(ChainKind.Near, assetInfo.contractId),
						args.amount,
					),
				{
					timeout: typeof window !== "undefined" ? 10_000 : 3000,
					errorInstance: new OmniWithdrawalApiFeeRequestTimeoutError(),
				},
			);
			// This adds a safeguard against insufficient UTXOs on the connector contract.
			// It cannot guarantee full protection, there is always a potential race condition—
			// but it helps reduce the chance of withdrawals getting stuck due to missing UTXOs.
			if (fee.insufficient_utxo) {
				throw new InsufficientUtxoForOmniBridgeWithdrawalError(
					assetInfo.blockchain,
				);
			}

			assert(
				fee.min_amount !== null &&
					fee.min_amount !== undefined &&
					BigInt(fee.min_amount) > 0n,
				`Invalid min amount value for a UTXO chain withdrawal: expected > 0, got ${fee.min_amount}`,
			);
			const minAmount = BigInt(fee.min_amount);
			const utxoMaxGasFee = getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.OmniBridge,
				"utxoMaxGasFee",
			);
			const utxoProtocolFee = getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.OmniBridge,
				"utxoProtocolFee",
			);
			assert(
				utxoMaxGasFee !== undefined && utxoMaxGasFee > 0n,
				`Invalid Omni Bridge utxo max gas fee: expected > 0, got ${utxoMaxGasFee}`,
			);
			assert(
				utxoProtocolFee !== undefined && utxoProtocolFee > 0n,
				`Invalid Omni Bridge utxo protocol fee: expected > 0, got ${utxoProtocolFee}`,
			);

			if (!args.skipMinAmountValidation) {
				// args.amount is without fee, we need to pass an amount with fee
				const actualAmountWithFee =
					args.amount + utxoMaxGasFee + utxoProtocolFee;
				if (actualAmountWithFee < minAmount) {
					throw new MinWithdrawalAmountError(
						minAmount,
						actualAmountWithFee,
						args.assetId,
					);
				}
			}
```

**File:** packages/intents-sdk/src/sdk.ts (L334-364)
```typescript
	public async createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
		referral?: string;
		logger?: ILogger;
	}): Promise<IntentPrimitive[]> {
		for (const bridge of this.bridges) {
			if (await bridge.supports(args.withdrawalParams)) {
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - args.feeEstimation.amount
					: args.withdrawalParams.amount;

				await bridge.validateWithdrawal({
					assetId: args.withdrawalParams.assetId,
					amount: actualAmount,
					destinationAddress: args.withdrawalParams.destinationAddress,
					destinationMemo: args.withdrawalParams.destinationMemo,
					feeEstimation: args.feeEstimation,
					routeConfig: args.withdrawalParams.routeConfig,
					logger: args.logger,
				});

				return bridge.createWithdrawalIntents({
					withdrawalParams: {
						...args.withdrawalParams,
						amount: actualAmount,
					},
					feeEstimation: args.feeEstimation,
					referral: args.referral ?? this.referral,
				});
			}
```
