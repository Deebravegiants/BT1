### Title
`validateEthAddress`/`compareAddresses` permit withdrawals to unspendable precompile addresses (e.g. `0x…01`) on EVM chains via OmniBridge - (File: `packages/intents-sdk/src/lib/validateAddress.ts`, `packages/intents-sdk/src/lib/compareAddresses.ts`)

### Summary
`validateEthAddress` only special-cases the zero address and the `0x…dead` burn address; every other syntactically valid checksum address — including well-known EVM precompile addresses such as `0x0000000000000000000000000000000000000001` (the `ecrecover` precompile) — passes as a valid `destinationAddress`. `compareAddresses` only blocks a destination equal to the bridged token's own contract address, so it does not catch this case either. As a result, `OmniBridge.validateWithdrawal` accepts a withdrawal whose destination is an address with no known private key, and the bridge connector delivers the native/ERC‑20 value there with no possible recovery.

### Finding Description
The broken equality is: *"destination is an account capable of receiving/controlling the withdrawn asset"* vs what is actually checked, which is only *"destination is not `0x0`, not `0x…dead`, and not the bridged token's own contract address."*

Code path:
- `validateAddress(address, blockchain)` dispatches EVM chains (`Chains.Ethereum`, etc.) to `validateEthAddress`: [1](#0-0) 
which rejects only two specific literals and otherwise accepts anything that passes `isAddress(address, {strict:true})` — this includes `0x0000000000000000000000000000000000000001`.

- `OmniBridge.validateWithdrawal` calls `validateAddress` for format, then `compareAddresses` only to block the token's own address: [2](#0-1) 

- `compareAddresses` for EVM chains does a plain `getAddress(a) === getAddress(b)` comparison against the bridged token address only, with no denylist of precompile/burn addresses: [3](#0-2) 

- The repo's own test suite confirms this is accepted, not rejected: `validateWithdrawal` with `destinationAddress: "0x0000000000000000000000000000000000000001"` resolves successfully (`.resolves.toBeUndefined()`): [4](#0-3) 

Attacker input: an ordinary user (or an integrator forwarding a counterparty-supplied string) calls `IntentsSDK.createWithdrawalIntents` / `processWithdrawal` with `destinationAddress = "0x0000000000000000000000000000000000000001"` and a valid `routeConfig` for Ethereum (or any EVM chain routed through OmniBridge). `validateWithdrawal` passes both `validateAddress` and `compareAddresses`, the intent is built and signed via `createWithdrawIntentsPrimitive`/`deriveOmniWithdrawIntentParams`, and the Omni Bridge connector on the destination EVM chain executes a value transfer (native ETH or ERC‑20) to `0x…01`. Address `0x…01` is reserved for the `ecrecover` precompile; no private key exists for it, so any value delivered there is permanently unrecoverable — functionally identical to (or worse than) the already-blocked `0x…dead` burn address, which the code explicitly treats as dangerous but only for that one literal.

### Impact Explanation
Funds (native ETH or bridged ERC‑20 tokens) are debited from the user's intents-controlled balance, signed away via a validly-constructed withdrawal intent, and misrouted to a destination address that no party can ever control or recover from — matching "funds delivered to a wrong address/chain/contract with no recovery" (Critical) since there is no manual-intervention recovery path (unlike a contract that merely "gets stuck," here there is no owner/key at all). This is repeatable by any unprivileged user for any EVM-routed OmniBridge withdrawal, once per withdrawal call.

### Likelihood Explanation
No special preconditions: the attacker only needs a normal intents balance and a standard OmniBridge withdrawal route to any supported EVM chain (Ethereum, Optimism, BNB, Polygon, etc.). The check that fails is purely format+self-address validation, both of which are trivially satisfied by `0x…01`. Cost is just the withdrawal amount itself (self-inflicted loss) or, more importantly, this same address string could be supplied by a compromised/malicious counterparty whose destination address an integrator blindly forwards into the SDK (per the rules, integrators forwarding untrusted `destinationAddress` strings are in-scope attacker capability). Fully reproducible and deterministic.

### Recommendation
Extend `validateEthAddress` (and equivalent checks for other EVM-like chains dispatched through it) to reject all standard Ethereum precompile addresses (`0x…01` through `0x…09`, and any chain-specific extensions) in addition to the zero address and `0x…dead`, mirroring the existing burn-address denylist approach rather than relying solely on `compareAddresses` against the bridged token's own address.

### Proof of Concept
```ts
// vitest, mocks only HTTP/RPC via existing test helpers (nearFailoverRpcProvider, omniBridgeUtils spies)
it("BROKEN EQUALITY: precompile address 0x...01 is currently accepted as a valid EVM destination", async () => {
  const nearProvider = nearFailoverRpcProvider({ urls: PUBLIC_NEAR_RPC_URLS });
  const bridge = new OmniBridge({ envConfig: configsByEnvironment.production, nearProvider });

  // LHS: attacker-controlled destinationAddress
  const destinationAddress = "0x0000000000000000000000000000000000000001";

  // RHS (claimed invariant): destination should be a spendable account
  // isAddress(destinationAddress, {strict:true}) === true  -> passes format check
  // compareAddresses(tokenAddress, destinationAddress, "eip155:1") === false -> not blocked as "token's own address"
  // => validateWithdrawal currently resolves instead of throwing

  await expect(
    bridge.validateWithdrawal({
      assetId: "nep141:lsd-usdt.rhealab.near",
      amount: 1_000_000n,
      destinationAddress,
      feeEstimation: {
        amount: 0n,
        quote: null,
        underlyingFees: {
          [RouteEnum.OmniBridge]: { relayerFee: 0n, storageDepositFee: 0n },
        },
      },
      routeConfig: createOmniBridgeRoute(Chains.Ethereum),
    }),
  ).resolves.toBeUndefined(); // demonstrates the gap: should instead reject with InvalidDestinationAddressForWithdrawalError
});
```
This matches the existing test at [4](#0-3) , which already documents (as passing/expected) that `0x…01` is accepted — confirming the invariant "destination must be a controllable account" is currently broken.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L105-113)
```typescript
function validateEthAddress(address: string) {
	if (
		address === "0x0000000000000000000000000000000000000000" ||
		address.toLowerCase() === "0x000000000000000000000000000000000000dead"
	) {
		return false;
	}
	return isAddress(address, { strict: true });
}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L358-396)
```typescript
		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}

		const omniChainKind = caip2ToChainKind(assetInfo.blockchain);
		assert(
			omniChainKind !== null,
			`Chain ${assetInfo.blockchain} is not supported by Omni Bridge`,
		);

		const destTokenOmniAddress = await this.getCachedDestinationTokenAddress(
			assetInfo.contractId,
			omniChainKind,
		);
		if (destTokenOmniAddress === null) {
			throw new TokenNotFoundInDestinationChainError(
				args.assetId,
				assetInfo.blockchain,
			);
		}

		const destTokenAddress = getAddress(destTokenOmniAddress);
		if (
			compareAddresses(
				destTokenAddress,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				destTokenAddress,
				args.assetId,
			);
		}
```

**File:** packages/intents-sdk/src/lib/compareAddresses.ts (L18-36)
```typescript
		switch (blockchain) {
			case Chains.Ethereum:
			case Chains.Optimism:
			case Chains.BNB:
			case Chains.Gnosis:
			case Chains.Polygon:
			case Chains.Monad:
			case Chains.LayerX:
			case Chains.Adi:
			case Chains.Base:
			case Chains.Arbitrum:
			case Chains.Avalanche:
			case Chains.Berachain:
			case Chains.Plasma:
			case Chains.Scroll:
			case Chains.Abstract:
			case Chains.HyperCore:
			case Chains.HyperEvm:
				return getAddress(a) === getAddress(b);
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts (L1281-1299)
```typescript
			await expect(
				bridge.validateWithdrawal({
					assetId: "nep141:lsd-usdt.rhealab.near",
					amount: 1_000_000n,
					destinationAddress: "0x0000000000000000000000000000000000000001",
					feeEstimation: {
						amount: 0n,
						quote: null,
						underlyingFees: {
							[RouteEnum.OmniBridge]: {
								relayerFee: 0n,
								storageDepositFee: 0n,
							},
						},
					},
					routeConfig: createOmniBridgeRoute(Chains.Ethereum),
				}),
			).resolves.toBeUndefined();
		});
```
