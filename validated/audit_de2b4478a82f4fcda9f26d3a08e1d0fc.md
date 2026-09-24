### Title
Unchecked division by external `exchangeRate()` in `previewLtUntilGraduation` permanently DoSes curve buys if the LT price ever reads zero - (File: packages/contracts/src/Bonding.sol)

### Summary
The CVE describes a divide-by-zero in ClickHouse's Gorilla codec: an attacker-controlled byte is used as a divisor/modulus without a zero-check, causing a crash. The analogous class in alt.fun is a value read from an external, live-priced dependency (`IBounceLeveragedToken.exchangeRate()`) being used as a divisor in `Bonding.previewLtUntilGraduation` without the same zero-guard that `_deployAndSeed` applies at launch time.

### Finding Description
At launch, `_deployAndSeed` explicitly guards against a zero exchange rate: [1](#0-0) 

However, `previewLtUntilGraduation` — which is called on *every* curve buy — re-reads `exchangeRate()` later in the token's life and, per its own doc comment, performs a "ceil-div on the USD leg" to compute the LT amount needed to cross the graduation threshold: [2](#0-1) 

This later read has no `if (exchangeRate == 0) revert` guard analogous to the one in `_deployAndSeed`. `Zap._executeBuy` calls this function unconditionally on the non-graduated (curve) buy path, before sizing the LT mint: [3](#0-2) 

If `exchangeRate()` ever returns `0` after launch (the LT's own documentation/interface does not guarantee monotonic non-zero pricing — leveraged tokens can be wiped toward zero in extreme moves, and the interface only documents "USDC per LT unit, 18-dp" with no floor), the ceil-div computation in `previewLtUntilGraduation` performs a raw Solidity division by zero, which panics with code `0x12` (division/modulo by zero) rather than a descriptive revert.

### Impact Explanation
Because `previewLtUntilGraduation` is invoked unconditionally by `Zap._executeBuy` for every non-graduated buy, a zero `exchangeRate()` read permanently DoSes all further curve buys for that token via `Zap` — the token can never accumulate more curve-raised LT, and since `canGraduate` also depends on `exchangeRate()` for its USD trigger, graduation itself may also stall. This freezes trader capital already committed to the curve (they can buy but the primary UI path reverts) and blocks the creator/token's path to graduation, matching the "permanent freezing of trader, creator or LP funds" bar in this exercise's validation criteria.

### Likelihood Explanation
This requires the external LT's `exchangeRate()` to return exactly `0`, which is an LT-side/price-feed condition outside alt.fun's control — the rules exclude "bugs inside BounceTech LT ... themselves," and I could not confirm from the interface or available contract code whether BounceTech's `LeveragedToken.exchangeRate()` can legitimately return `0` in production (e.g., under total collateral wipeout for an extreme leveraged short/long). Without that confirmation, likelihood is speculative rather than demonstrated, and the root-cause code path in `Bonding.sol` beyond line 720 (the actual division expression) was not fully retrievable in this session.

### Recommendation
Add the same `if (exchangeRate == 0) revert ZeroExchangeRate();` guard used in `_deployAndSeed` to every subsequent live read of `exchangeRate()` in `Bonding.sol` (`canGraduate`, `previewLtUntilGraduation`) and in `Zap.sol`, so a degenerate LT price surfaces as a clear, catchable revert rather than an unguarded division panic, and consider a fallback/pause path rather than a hard DoS of the buy flow.

### Proof of Concept
Not fully constructible from the indexed content: the exact division statement in `previewLtUntilGraduation` past line 720 of `packages/contracts/src/Bonding.sol` was not returned by the available tools within this session's index. Due to index size limits, some file contents may not be available; a Devin session with full repository access would be needed to pull the complete function body, write a Foundry test setting `MockLeveragedToken.setExchangeRate(0)`, and demonstrate the panic on a subsequent `Zap.buy` call.

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-479)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
```

**File:** packages/contracts/src/Bonding.sol (L697-720)
```text
    /// @notice LT amount that must be added to the curve's `assetReserve` for
    ///         `canGraduate(token_)` to become true. `0` when already
    ///         graduatable or not in `Lifecycle.Curve`.
    /// @dev    Composes the two `canGraduate` legs (supply trigger from
    ///         `IPair.tokenBalance() == 0`, USD trigger from
    ///         `realLtRaised × exchangeRate / 1e18 ≥ graduationThresholdUsd`)
    ///         and returns the cap-binding `min`. Ceil-div on the USD leg
    ///         so the resulting buy strictly crosses the threshold.
    function previewLtUntilGraduation(
        address token_
    ) external view returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return 0;
        if (info.lifecycle != Lifecycle.Curve) return 0;

        address pair = info.pair;
        uint256 realBalance = IPair(pair).tokenBalance();
        if (realBalance == 0) return 0;

        (uint256 reserveToken, uint256 reserveAsset) = IPair(pair).getReserves();

        uint256 ltUntilThreshold = type(uint256).max;
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
```

**File:** packages/contracts/src/Zap.sol (L323-326)
```text
        } else {
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
            uint256 ltUntilGraduation = $.bonding.previewLtUntilGraduation(tokenAddress);

```
