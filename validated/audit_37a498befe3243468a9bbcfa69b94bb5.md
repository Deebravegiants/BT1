Confirmed there's no whitelist/validation of `auroraEngineContractId` anywhere in the codebase — it's accepted as a free-form string from the caller via `createVirtualChainRoute()` / `VirtualChainRouteConfig` and used directly.

### Title
Unvalidated `auroraEngineContractId` lets caller redirect Virtual-Chain withdrawal funds to an arbitrary NEAR account while `describeWithdrawal` unconditionally reports completion - (File: packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts)

### Summary
The `AuroraEngineBridge` withdrawal flow builds an `ft_withdraw` intent whose `receiver_id` (and, in the proxy-token case, the `msg` routing target) is taken verbatim from the caller-supplied `routeConfig.auroraEngineContractId`. Nothing in `supports()`, `validateWithdrawal()`, or `createWithdrawalIntents()` checks that this value is actually a legitimate Aurora Engine bridge contract that custodies/forwards the token to the destination chain. Combined with `describeWithdrawal()` unconditionally returning `{ status: "completed", txHash: null }`, an integrator using this route with a bad or malicious `auroraEngineContractId` will have its tokens transferred to a non-custodial account while the SDK reports the withdrawal as successfully completed.

### Finding Description
`VirtualChainRouteConfig` defines: [1](#0-0) 

`auroraEngineContractId` and `proxyTokenContractId` are plain `string`/`string | null` fields — there is no reference to a fixed/whitelisted set of Aurora Engine contract IDs anywhere in the SDK.

`supports()` only checks that the asset is NEP-141; it performs no validation of `auroraEngineContractId`: [2](#0-1) 

`validateWithdrawal()` only validates that the *destination EVM address* is well-formed; it never checks the NEAR-side `auroraEngineContractId`: [3](#0-2) 

`createWithdrawIntentPrimitive()` then uses that same unvalidated value as the `receiver_id` of the `ft_withdraw` intent — i.e., the account that will actually receive/custody the withdrawn tokens on NEAR before (supposedly) bridging them to the virtual chain: [4](#0-3) 

Finally, regardless of whether the funds actually reached the destination chain, `describeWithdrawal()` is hard-coded to report success: [5](#0-4) 

This is the same equality-break pattern as the referenced Sense `redeem` bug: an address/contract that is supposed to be a trusted custodian of the bridged funds (`d` in Sense, `auroraEngineContractId`/`proxyTokenContractId` here) is fully attacker/caller-controlled and unchecked against any canonical value, and the "outcome" reported by the code (`redeem` succeeding in Sense; `status: "completed"` here) does not reflect what actually happened on-chain.

### Impact Explanation
If `routeConfig.auroraEngineContractId` (or `proxyTokenContractId`) is set to an account that is not the genuine Aurora Engine bridge contract for the target virtual chain — whether through misconfiguration, a compromised/stale config, or a malicious integrator-supplied route — the withdrawn tokens are transferred via `ft_transfer`/`ft_transfer_call` to that account instead of being forwarded to the user's destination address on the virtual chain. Because `describeWithdrawal()` never checks the actual outcome on the virtual chain and unconditionally returns `completed`, any code relying on the SDK's withdrawal-completion signal (e.g., `waitForWithdrawalCompletion`) will believe the withdrawal succeeded even though the funds never reached the intended destination. This matches the "High" category: a withdrawal stuck with no automatic recovery path, combined with a status misreport that could cause an integrator to treat the withdrawal as settled and credit/release downstream funds it should not.

### Likelihood Explanation
This requires the SDK caller (integrator) to supply a `VirtualChainRouteConfig` with an incorrect/non-canonical `auroraEngineContractId`. Since the SDK does not hardcode or validate this value against a known-good Aurora Engine registry, this can occur from a configuration bug, a stale/incorrect value, or a maliciously crafted route passed to `processWithdrawal`/`createWithdrawalIntents` — there is no code path stopping it. Given the field is explicitly documented as caller-supplied ("Requires explicit `routeConfig` with `auroraEngineContractId`"), the likelihood of this being exercised via normal integration mistakes (not requiring any admin/relayer misbehavior) is realistic.

### Recommendation
- Validate `auroraEngineContractId` (and `proxyTokenContractId`) against a known allow-list of legitimate Aurora Engine bridge contracts per virtual chain, similar to how `OmniBridge` validates destination token addresses.
- Make `describeWithdrawal()` for `AuroraEngineBridge` actually verify on-chain that the deposit was accepted/forwarded (e.g., via Aurora Engine's deposit confirmation or a destination-chain balance/tx check) rather than unconditionally returning `completed`.

### Proof of Concept
1. An integrator (or a route-config supplied by an untrusted upstream source) calls:
```ts
sdk.processWithdrawal({
  withdrawalParams: {
    assetId: "nep141:<some-token>.near",
    amount: 1000000n,
    destinationAddress: "0x...",
    feeInclusive: false,
    routeConfig: createVirtualChainRoute("malicious-account.near", null),
  }
});
```
2. `AuroraEngineBridge.supports()` and `validateWithdrawal()` accept this without checking that `malicious-account.near` is a genuine Aurora Engine contract (`aurora-engine-bridge.ts:60-142`).
3. `createWithdrawIntentPrimitive()` sets `receiver_id: "malicious-account.near"` on the `ft_withdraw` intent (`aurora-engine-bridge-utils.ts:26-37`), so tokens are transferred there instead of a real bridge contract.
4. `malicious-account.near` need not forward anything to the target chain.
5. `AuroraEngineBridge.describeWithdrawal()` still returns `{ status: "completed", txHash: null }` (`aurora-engine-bridge.ts:220-222`), so any caller of `sdk.waitForWithdrawalCompletion` / `processWithdrawal` sees the withdrawal marked as completed even though funds never reached the destination chain.

### Citations

**File:** packages/intents-sdk/src/shared-types.ts (L270-274)
```typescript
export type VirtualChainRouteConfig = {
	route: RouteEnum["VirtualChain"];
	auroraEngineContractId: string;
	proxyTokenContractId: string | null;
};
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L60-77)
```typescript
	async supports(
		params: Pick<WithdrawalParams, "assetId" | "routeConfig">,
	): Promise<boolean> {
		if (params.routeConfig == null || !this.is(params.routeConfig)) {
			return false;
		}

		const assetInfo = parseDefuseAssetId(params.assetId);
		const isValid = assetInfo.standard === "nep141";

		if (!isValid) {
			throw new UnsupportedAssetIdError(
				params.assetId,
				"`assetId` does not match `routeConfig`.",
			);
		}
		return isValid;
	}
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L125-142)
```typescript
	/**
	 * Aurora Engine bridge doesn't have withdrawal restrictions.
	 */
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
	}): Promise<void> {
		if (validateAddress(args.destinationAddress, Chains.Ethereum) === false) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				"virtual-chain",
			);
		}

		return;
	}
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L220-222)
```typescript
	async describeWithdrawal(): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: null };
	}
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge-utils.ts (L11-51)
```typescript
export function createWithdrawIntentPrimitive(params: {
	assetId: string;
	auroraEngineContractId: string;
	proxyTokenContractId: string | null;
	destinationAddress: string;
	amount: bigint;
	storageDeposit: bigint;
}): IntentFtWithdraw {
	const { contractId: tokenAccountId, standard } = utils.parseDefuseAssetId(
		params.assetId,
	);
	assert(standard === "nep141", "Only NEP-141 is supported");

	// Most cases
	if (params.proxyTokenContractId == null) {
		return {
			intent: "ft_withdraw",
			token: tokenAccountId,
			receiver_id: params.auroraEngineContractId,
			amount: params.amount.toString(),
			msg: makeAuroraEngineDepositMsg(params.destinationAddress),
			storage_deposit:
				params.storageDeposit > 0n
					? params.storageDeposit.toString()
					: undefined,
			min_gas: MIN_GAS_AMOUNT,
		};
	}

	//  Flow for transferring a base token to a virtual chain with a non-standard (non-ETH) base token
	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: params.proxyTokenContractId,
		amount: params.amount.toString(),
		msg: `${params.auroraEngineContractId}:${makeAuroraEngineDepositMsg(params.destinationAddress)}`,
		storage_deposit:
			params.storageDeposit > 0n ? params.storageDeposit.toString() : undefined,
		min_gas: MIN_GAS_AMOUNT_NON_STANDARD_DECIMALS,
	};
}
```
