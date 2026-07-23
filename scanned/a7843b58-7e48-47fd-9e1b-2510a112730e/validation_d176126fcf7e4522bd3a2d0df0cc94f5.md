### Title
Missing `baseFeedId != quoteFeedId` guard in synthetic-ratio mode locks the pool to a 1:1 price — (`File: smart-contracts-poc/contracts/AnchoredPriceProvider.sol`)

---

### Summary

`AnchoredPriceProvider` supports a two-feed "synthetic ratio" mode (`quoteFeedId != bytes32(0)`) that computes `mid = price(baseFeedId) / price(quoteFeedId)`. Neither the provider constructor nor `AnchoredProviderFactory.createAnchoredProvider` validates that `baseFeedId != quoteFeedId`. When both IDs are identical the ratio collapses to `1e8` (1.0 in 8-decimal terms) for every block, regardless of actual market prices, and the pool executes all swaps at a permanently wrong 1:1 rate.

---

### Finding Description

`AnchoredPriceProvider._getBidAndAskPrice` reads both legs independently and divides:

```solidity
// AnchoredPriceProvider.sol lines 258-271
function _getBidAndAskPrice() internal returns (uint128, uint128) {
    (uint256 mid, uint256 spreadBps, , bool ok) = _readLeg(baseFeedId);
    if (!ok) return (0, type(uint128).max);

    bytes32 _quote = quoteFeedId;
    if (_quote != bytes32(0)) {
        (uint256 mid2, uint256 spreadBps2, , bool ok2) = _readLeg(_quote);
        if (!ok2 || mid2 == 0) return (0, type(uint128).max);
        mid = Math.mulDiv(mid, ORACLE_DECIMALS, mid2);   // mid1 / mid2
        spreadBps += spreadBps2;
    }
    return _computeBidAsk(mid, spreadBps);
}
``` [1](#0-0) 

When `baseFeedId == quoteFeedId`, both `_readLeg` calls hit the same oracle slot, returning the same `mid` value `P`. The division becomes `Math.mulDiv(P, 1e8, P) = 1e8`, so the pool always receives a mid-price of exactly 1.0 (in 8-decimal terms), with `spreadBps` doubled. The constructor only guards token addresses, not feed IDs:

```solidity
// AnchoredPriceProvider.sol line 146
require(_baseToken != address(0) && _quoteToken != address(0) && _baseToken != _quoteToken);
``` [2](#0-1) 

`AnchoredProviderFactory.createAnchoredProvider` likewise performs no `baseFeedId != quoteFeedId` check before deploying the provider: [3](#0-2) 

The resulting provider passes `isProvider() == true` on the factory and satisfies the pool factory's token-match check (`token0()/token1()` are still distinct), so it can be legitimately registered as a pool's price provider.

---

### Impact Explanation

Every swap on a pool backed by such a provider executes at a fixed 1:1 rate (±doubled spread). For any pair where token0 ≠ token1 in value, arbitrageurs can drain the pool of the more valuable token by paying the cheaper one at par. LPs suffer direct, unbounded loss of principal proportional to the price divergence from 1:1. This matches the "bad-price execution" and "pool insolvency" impact categories.

---

### Likelihood Explanation

`createAnchoredProvider` is permissionless. A curator who copy-pastes the same feed ID into both `baseFeedId` and `quoteFeedId` (a plausible mistake when setting up a synthetic pair) produces a permanently broken provider with no on-chain signal of the error. The factory's envelope validation passes because it only checks `baseFeedId`'s class; the `quoteFeedId` is not class-validated at all. The misconfiguration is silent until swaps begin.

---

### Recommendation

Add the following guard in `AnchoredPriceProvider`'s constructor (and mirror it in `AnchoredProviderFactory.createAnchoredProvider`):

```solidity
// In AnchoredPriceProvider constructor, after storing baseFeedId/quoteFeedId:
if (_quoteFeedId != bytes32(0)) {
    require(_baseFeedId != _quoteFeedId, "SameFeedId");
}
```

This is the direct analog of the `DoubleTokenLexscrow` fix: just as `_tokenContract1 != _tokenContract2` must be enforced, `baseFeedId != quoteFeedId` must be enforced when synthetic-ratio mode is active.

---

### Proof of Concept

```solidity
// Pseudo-test (Foundry)
bytes32 FEED = keccak256("ETH/USD");

// Deploy provider with baseFeedId == quoteFeedId (no revert)
AnchoredPriceProvider p = new AnchoredPriceProvider(
    factory, oracle, FEED, FEED,   // <-- same feed both slots
    minMargin, maxStaleness, maxSpreadBps,
    false, 0, TOKEN0, TOKEN1
);

// Oracle reports ETH/USD = 2000 (8-decimal: 200_000_000_000)
oracle.setData(FEED, 200_000_000_000, 5, 0, block.timestamp);

// Provider returns mid = 200_000_000_000 / 200_000_000_000 = 1e8 (= 1.0)
// Pool prices TOKEN0 at 1:1 against TOKEN1 regardless of actual 2000:1 ratio
(uint128 bid, uint128 ask) = p.getBidAndAskPrice();
// bid ≈ ask ≈ Q64  (1.0 in Q64.64)

// Attacker swaps 1 TOKEN1 (worth $1) and receives ~1 TOKEN0 (worth $2000)
// Repeat until pool is drained of TOKEN0
``` [1](#0-0) [4](#0-3)

### Citations

**File:** smart-contracts-poc/contracts/AnchoredPriceProvider.sol (L146-146)
```text
        require(_baseToken != address(0) && _quoteToken != address(0) && _baseToken != _quoteToken);
```

**File:** smart-contracts-poc/contracts/AnchoredPriceProvider.sol (L258-272)
```text
    function _getBidAndAskPrice() internal returns (uint128, uint128) {
        (uint256 mid, uint256 spreadBps, , bool ok) = _readLeg(baseFeedId);
        if (!ok) return (0, type(uint128).max);

        bytes32 _quote = quoteFeedId;
        if (_quote != bytes32(0)) {
            (uint256 mid2, uint256 spreadBps2, , bool ok2) = _readLeg(_quote);
            if (!ok2 || mid2 == 0) return (0, type(uint128).max);
            // Synthetic ratio (8-decimal): mid1 / mid2. Relative uncertainties of a ratio add.
            mid = Math.mulDiv(mid, ORACLE_DECIMALS, mid2);
            spreadBps += spreadBps2;
        }

        return _computeBidAsk(mid, spreadBps);
    }
```

**File:** smart-contracts-poc/contracts/AnchoredProviderFactory.sol (L156-195)
```text
    function createAnchoredProvider(
        address oracle,
        bytes32 baseFeedId,
        bytes32 quoteFeedId,
        uint256 minMargin,
        uint256 maxRefStaleness,
        uint16  maxSpreadBps,
        bool    mutableParams,
        int256  marginStep,
        address baseToken,
        address quoteToken
    ) external override returns (address provider) {
        if (!_oracles.contains(oracle)) revert OracleNotAllowed(oracle);

        // Feeds without an explicit class fall back to the admin-configured DEFAULT_CLASS envelope.
        bytes32 classId = feedClass[baseFeedId];
        if (classId == bytes32(0)) classId = DEFAULT_CLASS;

        Envelope storage env = envelopes[classId];
        if (!env.exists) revert EnvelopeNotFound(classId);
        if (
            minMargin < env.minMarginMin || minMargin > env.minMarginMax
            || maxRefStaleness < env.stalenessMin || maxRefStaleness > env.stalenessMax
            || maxSpreadBps < env.maxSpreadMin || maxSpreadBps > env.maxSpreadMax
        ) revert ParamsOutOfEnvelope();

        AnchoredPriceProvider p = new AnchoredPriceProvider(
            address(this),
            oracle,
            baseFeedId,
            quoteFeedId,
            minMargin,
            maxRefStaleness,
            maxSpreadBps,
            mutableParams,
            marginStep,
            baseToken,
            quoteToken
        );

```
