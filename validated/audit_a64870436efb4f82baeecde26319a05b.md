Found the exact analog: `IntentGatewayContext.solverCodeCache` is a single process-global `Map<string, string>` keyed only by lowercased address, and `GasEstimator.buildStateOverride` reads/writes it with a key derived only from `getSolverAccountAddress(chain)` — the chain identifier is never part of the cache key. [1](#0-0) [2](#0-1) 

### Title
Cross-chain data leak via chain-unscoped `solverCodeCache` in `GasEstimator.buildStateOverride` - (File: sdk/packages/sdk/src/protocols/intents/GasEstimator.ts)

### Summary
This is directly analogous to the containerd CRI env-var leak (CVE-2021-21334): a cached value fetched for one execution context is later served, unchanged, for a *different* context that shares the same cache key but is not actually the same entity. In containerd, the cache key was the image reference but the leaked value (env vars) actually varied per-container; here the cache key is the solver account address, but the value (`getCode` bytecode) actually depends on which chain it was read from, since `getSolverAccountAddress(chain)` and `this.ctx.dest.client` both vary per destination chain within the same `IntentGatewayContext`/`GasEstimator` lifetime.

### Finding Description
`IntentGatewayContext.solverCodeCache` is declared as a flat `Map<string, string>` "keyed by lowercased address" with no chain dimension: [3](#0-2) 

`GasEstimator.buildStateOverride` is invoked per `chain` (the destination state-machine id passed into `estimateFillOrder`), and reads the solver contract address for that specific chain via `this.ctx.dest.configService.getSolverAccountAddress(chain)`. It then builds a cache key from *only* the address, not the chain:

```
const cacheKey = solverAccountContract.toLowerCase()
let solverCode = this.ctx.solverCodeCache.get(cacheKey)
if (!solverCode) {
    solverCode = await this.ctx.dest.client.getCode({ address: solverAccountContract })
    ...
    this.ctx.solverCodeCache.set(cacheKey, solverCode)
}
``` [4](#0-3) 

`IntentGatewayContext` is documented as shared across sub-modules "without duplicating initialisation logic," and its cache maps are explicitly described as shared, long-lived state: [5](#0-4) 

Because a CREATE2-deployed solver-account factory can (and in this codebase's own admitted pattern elsewhere — see `paymasterSupportsPermit2`'s prior chain-keyed-cache fix, `sdk/packages/simplex/docs/ai/decisions/2026-08-24-review-fixes-robust-bootstrap-chain-keyed-probe-no-dead-config.md`) produce the *same address at the same deployment slot on different chains* with *different bytecode* (different implementation, unmigrated/upgraded on one chain but not another, or simply address collision from a different factory), the cache silently returns bytecode from whichever chain first populated the key on subsequent estimates for a different chain. This is precisely the containerd bug-class: a resource keyed by an identifier that is not the full/unique context, so the wrong context's cached data crosses the trust boundary.

### Impact Explanation
The injected bytecode via `bundlerOverrides[accountAddress].code = solverCode` feeds directly into `eth_estimateUserOperationGas`, which determines `callGasLimit`, `verificationGasLimit`, `preVerificationGas`, and paymaster gas limits returned by `estimateFillOrder`. Wrong-chain bytecode being simulated as "how the solver account behaves" produces gas estimates that do not reflect the actual account logic on the target chain — this can under- or over-estimate gas, cause a live `fillOrder` to revert on-chain (because the real account logic differs from what was simulated), or produce systematically wrong relayer-fee/gas-cost quotes (`FillOrderEstimate.totalGasCostWei`, `totalGasInFeeToken`) that solvers and the SDK rely on to price fills. This is CWE-668 (exposure to wrong control sphere): a value derived under one chain's execution context is exposed to and acted upon in another chain's context, without the actor being aware. It does not directly move funds, but it corrupts fee/gas estimation integrity used to construct fills, which can lead to reverted fills (denial of service to a route) or mispriced solver bids.

### Likelihood Explanation
Requires a fairly specific condition — the same solver-account address existing (via CREATE2 or coincidence) on two different chains configured in the same `IntentGatewayContext`, with different bytecode at that address (e.g., unmigrated factory version, chain-specific implementation, or a redeploy on one chain only). This is plausible in a multi-chain solver operating fleet using deterministic deployment addresses, matching the same failure mode the codebase already fixed once for `paymasterSupportsPermit2` in the simplex filler (see the F5/chain-keyed-cache fix referenced in `sdk/packages/simplex/docs/ai/decisions/2026-08-24-review-fixes-robust-bootstrap-chain-keyed-probe-no-dead-config.md`), which strongly suggests this exact class of bug is a known recurring pattern in this codebase that was not (yet) fixed here.

### Recommendation
Scope `solverCodeCache` keys by chain, e.g. `` `${chain}:${solverAccountContract.toLowerCase()}` ``, matching the fix already applied to the paymaster support cache elsewhere in the repo.

### Proof of Concept
1. Configure `IntentGatewayContext` with two destination chains, A and B, where the solver-account factory deploys to the same address on both chains (CREATE2 with identical salt/init code) but chain B's deployment has since been upgraded/redeployed with different bytecode (or a different, unrelated contract happens to occupy that address on B).
2. Call `estimateFillOrder` for an order destined to chain A first — `buildStateOverride` calls `getCode` on chain A's client, caches chain A's bytecode under key `solverAccountContract.toLowerCase()`.
3. Call `estimateFillOrder` for an order destined to chain B using the same `GasEstimator`/`IntentGatewayContext` instance — `buildStateOverride` computes the same `cacheKey` (address only), finds a cache hit, and injects **chain A's bytecode** into the state override for the chain B estimation instead of fetching chain B's actual code.
4. The resulting gas estimate for the chain B fill is computed against the wrong account logic, producing an incorrect `FillOrderEstimate` that can cause a subsequent on-chain `fillOrder` on chain B to revert or be mispriced.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/types.ts (L146-152)
```typescript
/**
 * Shared runtime context passed to every IntentsV2 sub-module.
 *
 * All sub-modules (OrderPlacer, OrderExecutor, BidManager, etc.) receive a
 * reference to this object so they can share fee-token caches, storage
 * adapters, and chain clients without duplicating initialisation logic.
 */
```

**File:** sdk/packages/sdk/src/protocols/intents/types.ts (L153-180)
```typescript
export interface IntentGatewayContext {
	/** EVM chain on which orders are placed and escrowed. */
	source: IEvmChain
	/** EVM chain on which solvers fill orders and receive outputs. */
	dest: IEvmChain
	/** Hyperbridge coprocessor client used to fetch solver bids and submit UserOperations. */
	intentsCoprocessor?: IntentsCoprocessor
	/** URL of the ERC-4337 bundler endpoint for gas estimation and UserOp submission. */
	bundlerUrl?: string
	/**
	 * In-memory TTL cache keyed by state-machine ID.
	 * Stores fee-token address, decimals, and the timestamp of the last fetch.
	 */
	feeTokenCache: Map<string, { address: HexString; decimals: number; cachedAt: number }>
	/**
	 * In-memory cache of solver account contract bytecode, keyed by lowercased address.
	 * Used to inject solver code into state-overrides for gas estimation.
	 */
	solverCodeCache: Map<string, string>
	/** Persistent storage for ephemeral session keys generated per order. */
	sessionKeyStorage: ReturnType<typeof createSessionKeyStorage>
	/** Persistent storage for intermediate cancellation state (proofs, commitments). */
	cancellationStorage: ReturnType<typeof createCancellationStorage>
	/** Persistent storage for deduplication of already-submitted UserOperations. */
	usedUserOpsStorage: ReturnType<typeof createUsedUserOpsStorage>
	/** DEX-quote utility used for token pricing and gas-to-fee-token conversions. */
	swap: Swap
}
```

**File:** sdk/packages/sdk/src/protocols/intents/GasEstimator.ts (L540-562)
```typescript
		const solverAccountContract = this.ctx.dest.configService.getSolverAccountAddress(chain)
		if (solverAccountContract) {
			try {
				const cacheKey = solverAccountContract.toLowerCase()
				let solverCode = this.ctx.solverCodeCache.get(cacheKey)

				if (!solverCode) {
					solverCode = await this.ctx.dest.client.getCode({ address: solverAccountContract })
					if (solverCode && solverCode !== "0x") {
						this.ctx.solverCodeCache.set(cacheKey, solverCode)
					}
				}

				if (solverCode && solverCode !== "0x") {
					if (!bundlerOverrides[accountAddress]) {
						bundlerOverrides[accountAddress] = {}
					}
					bundlerOverrides[accountAddress].code = solverCode
				}
			} catch {
				// Ignore
			}
		}
```
