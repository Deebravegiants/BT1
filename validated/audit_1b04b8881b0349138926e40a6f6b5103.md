Found it. The `knownV2Gateways` cache in `getFillOptionsVersion` is keyed only by the gateway proxy address, with no chain/RPC dimension in the key, even though `PublicClient` (and thus the actual network being queried) is a separate argument. Since IntentGateway proxies are deployed at the same CREATE2 address across chains (the code's own comments confirm this design assumption), a gateway address resolved to v2 on one chain will be permanently read as v2 for that same address on **every other chain**, even one still running the legacy pre-`validUntil` implementation, without ever re-querying that chain's storage.

### Title
Cross-chain cache-key collision in `getFillOptionsVersion` causes `validUntil` bound to be silently dropped on legacy chains - ([File: sdk/packages/sdk/src/protocols/intents/fillOrderCodec.ts])

### Summary
`getFillOptionsVersion` caches its ERC-1967 implementation-slot lookup result in a module-level `Set` keyed solely by `gateway.toLowerCase()`, ignoring the chain the `PublicClient` is bound to. [1](#0-0) 

### Finding Description
`getFillOptionsVersion(client, gateway)` first checks the fast-path `CHAINS_WITHOUT_VALID_UNTIL` set keyed by `chainId`, then falls back to `knownV2Gateways`, a cache keyed only by gateway address: [2](#0-1) 

Because the IntentGateway proxies are deployed via CREATE2 at the same address on every EVM chain (explicitly assumed by `LEGACY_FILL_OPTIONS_IMPLEMENTATIONS`'s comment: "One entry covers every chain... the protocol contracts are CREATE2-deployed, so this is the implementation address on all of them"), the address alone does not uniquely identify a deployment. If the SDK ever resolves `gateway` to v2 for chain A (adds it to `knownV2Gateways`), then a subsequent call for the same `gateway` address on chain B — whose `CHAINS_WITHOUT_VALID_UNTIL` maintenance list has fallen behind reality, or which was never added to that manually-maintained set — will hit the cache and return v2 without ever calling `resolveImplementation`/`client.getStorageAt` against chain B's actual state. This is the same bug class as the CVE: a security-relevant version/validity check is performed and cached once, then reused for a different underlying resource (a different chain's deployment) that was never actually checked, because the cache key doesn't capture all the state that determines correctness.

This function is used to select the ABI shape for `fillOrder`, specifically whether the `validUntil` expiry field is included in the encoded call: [3](#0-2) 

### Impact Explanation
If a stale/incorrect v2 verdict is served from the cross-chain-polluted cache for a chain whose gateway is actually still on the legacy v1 implementation, `encodeFillOrder` will emit a v2-shaped call. Per the code's own doc comment, on a v1 gateway the `validUntil` field is either dropped or (in the reverse mis-cache direction) simply never enforced on-chain "and no check on the other side. That is a real loss of protection." A filler/relayer or solver relying on the SDK's version detection could dispatch a `fillOrder` transaction whose expiry bound is not actually honored by the destination contract, allowing a fill to execute after the order should have expired — a loss of a caller-relied-upon safety bound in the intents fill path, reachable by any solver/relayer submitting a fill through the SDK.

### Likelihood Explanation
Exploitability depends on the IntentGateway proxy address actually colliding across chains (a documented, deliberate deployment property) and on at least one chain lagging behind another in the `validUntil` upgrade — a state explicitly anticipated by the existence of the manually maintained `CHAINS_WITHOUT_VALID_UNTIL` set, which the comments acknowledge must be kept in sync ("Delete a chain from this set when its gateway is redeployed"). Any staleness or omission in that list, combined with the module-global (non-chain-scoped) `knownV2Gateways` cache, triggers the cross-chain bleed without any malicious action — this is a correctness/soundness bug in the SDK's cache invalidation, not solely an admin/ops mistake, since the cache mechanism itself has no chain dimension.

### Recommendation
Key `knownV2Gateways` by `(chainId, gateway)` rather than by `gateway` alone, mirroring the chain-scoping already used for `CHAINS_WITHOUT_VALID_UNTIL`.

### Proof of Concept
1. Call `getFillOptionsVersion(clientForChainA, GATEWAY)` where chain A's gateway at `GATEWAY` has been upgraded to the current implementation → function resolves v2 and adds `GATEWAY.toLowerCase()` to `knownV2Gateways`.
2. Call `getFillOptionsVersion(clientForChainB, GATEWAY)` where chain B has the same `GATEWAY` address but is still running the legacy implementation and is not present in `CHAINS_WITHOUT_VALID_UNTIL`.
3. The second call hits `knownV2Gateways.has(key)` and returns `2` immediately, without querying chain B's storage at all, per [4](#0-3) .
4. `encodeFillOrder(order, options, 2)` on chain B then encodes a v2 call including `validUntil`, but chain B's actual legacy contract does not enforce/understand that field, silently dropping the intended expiry protection on that route.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/fillOrderCodec.ts (L104-150)
```typescript
/**
 * Gateways already resolved to v2, keyed by proxy address.
 *
 * Only v2 answers are cached, and that asymmetry is deliberate. A deployment can move from
 * legacy to current but never back, so a v2 result is true forever, while caching a v1 result
 * would pin the old encoding across the very upgrade that changes it — the proxy address does
 * not move, so nothing would ever invalidate it. A still-legacy gateway therefore costs one
 * storage read per fill, and an upgraded one costs none.
 */
const knownV2Gateways = new Set<string>()

/** Test seam: drop memoised detection results. */
export function resetFillOptionsVersionCache(): void {
	knownV2Gateways.clear()
}

/** The address the ERC-1967 proxy delegates to, or the gateway itself if it is not a proxy. */
async function resolveImplementation(client: PublicClient, gateway: HexString): Promise<HexString> {
	const slot = await client.getStorageAt({ address: gateway, slot: ERC1967_IMPLEMENTATION_SLOT })
	if (!slot || slot.length < 66) return gateway
	const addr = `0x${slot.slice(-40)}` as HexString
	return /^0x0{40}$/.test(addr) ? gateway : addr
}

/**
 * Works out which `FillOptions` shape a gateway accepts from the implementation it delegates to.
 *
 * EIP-1967 standardises three slots, all holding addresses — there is no version field to read,
 * and the contract deliberately does not carry one either: a hand-maintained version constant is
 * a second source of truth that has to be bumped on the right upgrade. The implementation address
 * is the value the proxy already updates, so it is what identifies the deployed code.
 */
export async function getFillOptionsVersion(client: PublicClient, gateway: HexString): Promise<FillOptionsVersion> {
	// Checked before the slot read: on a chain that has not been redeployed the implementation
	// address tells us nothing useful, and skipping the read saves a round trip.
	const chainId = client.chain?.id
	if (chainId !== undefined && CHAINS_WITHOUT_VALID_UNTIL.has(chainId)) return 1

	const key = gateway.toLowerCase()
	if (knownV2Gateways.has(key)) return 2

	const implementation = await resolveImplementation(client, gateway)
	if (LEGACY_FILL_OPTIONS_IMPLEMENTATIONS.has(implementation.toLowerCase())) return 1

	knownV2Gateways.add(key)
	return 2
}
```

**File:** sdk/packages/sdk/src/protocols/intents/fillOrderCodec.ts (L152-174)
```typescript
/**
 * ABI-encodes a `fillOrder` call in the shape the target gateway understands.
 *
 * On a v1 gateway `validUntil` is dropped — there is nowhere to put it and no check on the
 * other side. That is a real loss of protection, so callers that rely on the bound should
 * surface it rather than assume it took effect.
 */
export function encodeFillOrder(order: Order, options: FillOptions, version: FillOptionsVersion): HexString {
	if (version === 2) {
		return encodeFunctionData({
			abi: IntentGatewayV2ABI,
			functionName: "fillOrder",
			args: [order as any, options as any],
		}) as HexString
	}

	const { relayerFee, nativeDispatchFee, outputs } = options
	return encodeFunctionData({
		abi: FILL_ORDER_V1_ABI,
		functionName: "fillOrder",
		args: [order as any, { relayerFee, nativeDispatchFee, outputs } as any],
	}) as HexString
}
```
