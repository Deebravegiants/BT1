Audit Report

## Title
Stale Updater Permissions Persist After `transferProviderOwnership`, Allowing Unauthorized `setConfidence` Calls — (`smart-contracts-poc/contracts/PriceProviderFactory.sol`, `smart-contracts-poc/contracts/AnchoredProviderFactory.sol`)

## Summary
`transferProviderOwnership` in both `PriceProviderFactory` and `AnchoredProviderFactory` updates `providerOwner` and the `_providersByCreator` enumerable sets but never clears the `isUpdater[provider][*]` mapping. Every address previously granted updater rights by the old owner retains the ability to call `setConfidence()` on the transferred provider indefinitely. Because there is no enumerable set for updaters, the new owner has no on-chain mechanism to discover or bulk-revoke these stale permissions, leaving the provider's `confidenceParam` — and therefore its bid/ask spread — exposed to manipulation by addresses the new owner does not control.

## Finding Description
**Storage layout (both factories):**
```solidity
mapping(address provider => address) public providerOwner;
mapping(address provider => mapping(address updater => bool)) public isUpdater;
```

**`transferProviderOwnership` (PriceProviderFactory L92–102, AnchoredProviderFactory L230–240):**
```solidity
providerOwner[provider] = newOwner;
_providersByCreator[previousOwner].remove(provider);
_providersByCreator[newOwner].add(provider);
// isUpdater[provider][*] is never touched
emit ProviderOwnershipTransferred(provider, previousOwner, newOwner);
```

**`_requireUpdater` (PriceProviderFactory L34–37, AnchoredProviderFactory L61–64):**
```solidity
if (msg.sender != providerOwner[provider] && !isUpdater[provider][msg.sender])
    revert NotProviderUpdater();
```

After transfer, `providerOwner[provider]` is `newOwner`, but `isUpdater[provider][staleUpdater]` remains `true`. The `_requireUpdater` check passes for any stale updater, so `setConfidence()` (PriceProviderFactory L130–142, AnchoredProviderFactory L262–274) succeeds, calling `PriceProvider.setConfidenceParam()` or `AnchoredPriceProvider.setConfidenceParam()` on the transferred provider.

**Exploit path:**
1. Owner A creates a provider and calls `grantUpdater(provider, updaterAddr)` → `isUpdater[provider][updaterAddr] = true`.
2. Owner A calls `transferProviderOwnership(provider, ownerB)` → `providerOwner[provider] = ownerB`; `isUpdater` unchanged.
3. Owner B is unaware of `updaterAddr` (no enumerable set; no event index by new owner).
4. After `CONFIDENCE_COOLDOWN` (1 minute) elapses, `updaterAddr` calls `factory.setConfidence([provider], [1_000_000])`.
5. `_requireUpdater` passes (stale entry still `true`); `setConfidenceParam(1_000_000)` executes.

**Why existing guards fail:** The 1-minute `CONFIDENCE_COOLDOWN` only rate-limits updates; it does not prevent unauthorized callers. `revokeUpdater` requires the new owner to know each stale address individually — impossible without off-chain log scanning. The existing test `testOldOwnerCannotUpdateAfterTransfer` only verifies the previous *owner* loses direct rights; it does not cover previously-granted updaters.

## Impact Explanation
**For `PriceProvider`:** `confidenceParam` directly scales the oracle spread with no clamp:
```solidity
uint256 adjustedSpread = spread * confidenceParam;
(uint256 bid, uint256 ask) = _getBidAskFrom(mid, adjustedSpread);
```
Setting `confidenceParam = 1_000_000` (CONFIDENCE_MAX, 100× multiplier) on a 5 bps oracle spread produces a ±5% bid/ask band. Every swap against a pool using this provider executes at the inflated spread — sellers receive a bid up to 5% below mid, buyers pay an ask up to 5% above mid. This is direct, quantifiable bad-price execution harming trader token balances.

**For `AnchoredPriceProvider` (MUTABLE_PARAMS = true):** `_shapedQuote` uses `confidenceParam` to compute a wider custom quote, which is then clamped outward by the reference band (`Math.min(refBid, cBid)` / `Math.max(refAsk, cAsk)`). A stale updater setting max confidence forces the shaped quote outside the reference band, causing the clamp to deliver `bidOut < refBid` and `askOut > refAsk` — a spread wider than the audited envelope, constituting bad-price execution bounded only by the oracle's reference uncertainty.

This matches the allowed impact gate: **bad-price execution — unclamped (PriceProvider) or envelope-exceeding (AnchoredPriceProvider) bid/ask quote reaches a pool swap.**

## Likelihood Explanation
The precondition — at least one updater granted before transfer — is a normal operational pattern explicitly supported by the factory's deployment scripts (`SetConfidence` script assumes a dedicated updater key). No malicious intent from the previous owner is required: a legitimately-granted updater key that is compromised after the transfer, or simply an updater the new owner is unaware of, is sufficient. The stale updater can repeat the attack every `CONFIDENCE_COOLDOWN` (1 minute) indefinitely. The new owner has no on-chain path to enumerate stale updaters without off-chain log analysis, making silent exploitation feasible.

## Recommendation
**Option A — epoch key (recommended):** Scope `isUpdater` to `(provider, ownerEpoch)` so permissions expire automatically on transfer:
```solidity
mapping(address provider => uint256) public ownerEpoch;
mapping(address provider => mapping(uint256 epoch => mapping(address updater => bool))) public isUpdater;
// In transferProviderOwnership:
ownerEpoch[provider]++;
```
`_requireUpdater` checks `isUpdater[provider][ownerEpoch[provider]][msg.sender]`.

**Option B — enumerable updater set:** Replace the plain mapping with an `EnumerableSet.AddressSet` per provider, and clear it in `transferProviderOwnership`:
```solidity
for each updater in _updatersByProvider[provider]: isUpdater[provider][updater] = false;
_updatersByProvider[provider].clear();
```

**Option C — caller-supplied revocation list:** Require the transferring owner to supply updaters to clear:
```solidity
function transferProviderOwnership(address provider, address newOwner, address[] calldata updatersToClear) external ...
```

## Proof of Concept
```solidity
// Foundry test sketch
function testStaleUpdaterAfterTransfer() public {
    address provider = factory.createPriceProvider(...);
    address staleUpdater = address(0xBEEF);

    // Owner A grants updater
    vm.prank(ownerA);
    factory.grantUpdater(provider, staleUpdater);

    // Owner A transfers to Owner B
    vm.prank(ownerA);
    factory.transferProviderOwnership(provider, ownerB);

    // Cooldown passes
    vm.warp(block.timestamp + 2 minutes);

    // Stale updater still succeeds — BUG
    vm.prank(staleUpdater);
    factory.setConfidence(toArray(provider), toArray(1_000_000));

    // confidenceParam is now at maximum — bid/ask spread inflated up to 100×
    assertEq(PriceProvider(provider).confidenceParam(), 1_000_000);
}
```
The call at step 4 succeeds because `isUpdater[provider][staleUpdater]` was never cleared, satisfying `_requireUpdater` despite `staleUpdater` having no relationship to `ownerB`.