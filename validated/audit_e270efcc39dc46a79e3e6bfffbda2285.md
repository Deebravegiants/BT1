### Title
Missing zero-`exchangeRate()` guard in `Zap._executeBuy` permanently DoSes curve buys once the reserve LT rebases to zero - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._executeBuy`'s pre-graduation branch calls `IBounceLeveragedToken(lt).baseToLtAmount(netUsdc)` and later `mint(...)` without ever checking whether the LT's `exchangeRate()` is zero. `baseToLtAmount`/`mint` both divide by `exchangeRate` internally [1](#0-0) . If the reserve LT (a rebasing-priced, potentially leveraged/inverse token per the design docs) rebases its `exchangeRate()` to `0`, every subsequent `Zap.buy` on that curve token reverts with a division-by-zero panic, permanently freezing the buy side of the bonding curve for that token — an analog of the external report's NULL/degenerate-value dereference causing unconditional DoS.

### Finding Description
`Zap._executeBuy`, on the pre-graduation path, sizes the mint using the LT's own conversion helper: [2](#0-1) 
and then unconditionally calls `mint`: [3](#0-2) 

Both `baseToLtAmount` and `mint` compute `(baseAmount * 1e18) / exchangeRate` under the hood [4](#0-3) . Nowhere in `_executeBuy` is `exchangeRate() == 0` checked before this call.

Contrast this with `Bonding.previewLtUntilGraduation`, which is called by `_executeBuy` on the very same buy path and explicitly treats `exchangeRate == 0` as a distinct, handled case: [5](#0-4) 

This shows the protocol's own code is aware that the LT's `exchangeRate()` can legitimately be `0` (BounceTech LTs are leveraged/inverse tokens whose price can rebase to zero on full liquidation of the underlying), yet only one of the two consumers of that value on the identical buy path defends against it. `Zap._executeBuy` does not, so once `exchangeRate()` reports `0`:
- `previewLtUntilGraduation` returns `type(uint256).max` for the threshold leg (correctly handled, no revert there).
- `Zap._executeBuy`'s `baseToLtAmount(netUsdc)` call (and the subsequent `mint`) reverts with an unhandled arithmetic panic, because `_exchangeRate` is the divisor.

Since `Zap.buy` is the only permissionless way for a trader to buy on the curve (per the in-scope reachable-surface rules), and the curve has no alternate buy venue pre-graduation, this bricks the buy side of the token unconditionally and indefinitely (until/unless the LT's rate recovers above zero, which for a fully-liquidated leveraged token may never happen).

### Impact Explanation
Once triggered, `Zap.buy` reverts on every call for the affected token — a permanent denial-of-service of the primary trading entry point. Curve token holders lose their only way to add fresh capital/exit-support via the intended venue; new participants cannot enter. `Zap.sell` still functions (the sell path only multiplies by `exchangeRate`, never divides), so this is not full fund loss, but it permanently and unconditionally freezes the buy side and — because `canGraduate`'s USD leg also degrades to `false` for a zero rate — can prevent the token from ever reaching the USD graduation trigger via ordinary buys, leaving it stuck pre-graduation with no way to top off liquidity through the intended path.

### Likelihood Explanation
This does not require a malicious actor or privileged caller — it is triggered purely by the reserve LT's price hitting zero, a state the codebase's own comments and `previewLtUntilGraduation` logic explicitly anticipate as reachable for BounceTech's rebasing leveraged tokens. Given `alt.fun`'s design deliberately allows arbitrary BounceTech LTs (including leveraged/inverse ones prone to full liquidation) as the curve's reserve asset, this is a realistic, protocol-design-level edge case rather than a contrived scenario.

### Recommendation
Add an explicit `exchangeRate() == 0` check in `Zap._executeBuy` (mirroring `Bonding.previewLtUntilGraduation`'s guard) before calling `baseToLtAmount`/`mint`, and revert with a clear, catchable error (e.g. `ZeroExchangeRate`) instead of letting the call fail with an opaque panic deep inside the LT. Consider also surfacing a dedicated "curve frozen — reserve asset repriced to zero" state so the UI/API can communicate this distinctly from ordinary slippage/floor reverts.

### Proof of Concept
1. Launch a token via `Zap.createToken` against a BounceTech LT `lt`.
2. Have `lt.exchangeRate()` fall to `0` (e.g., via a liquidation event on a leveraged/inverse LT, mirrored in tests by `lt.setExchangeRate(0)`).
3. Call `zap.buy(tokenAddr, usdcAmount, 0, address(0))` as any trader.
4. The call reaches `IBounceLeveragedToken(lt).baseToLtAmount(netUsdc)` [2](#0-1) , which performs `(baseAmount * 1e18) / 0` and reverts with an arithmetic panic (`0x12`).
5. Every subsequent `zap.buy` call for this token reverts identically — the buy side of the curve is permanently DoS'd, while `zap.sell` continues to function.

### Citations

**File:** packages/contracts/test/mocks/MockLeveragedToken.sol (L41-52)
```text
    function mint(
        address to,
        uint256 baseAmount,
        uint256
    ) external returns (uint256 ltAmount) {
        if (_minTransactionSize > 0 && baseAmount < _minTransactionSize) {
            revert BelowMinTransactionSize();
        }
        ERC20(baseAsset).transferFrom(msg.sender, address(this), baseAmount);
        ltAmount = baseToLtAmount(baseAmount);
        _mint(to, ltAmount);
    }
```

**File:** packages/contracts/test/mocks/MockLeveragedToken.sol (L67-77)
```text
    function baseToLtAmount(
        uint256 baseAmount
    ) public view returns (uint256) {
        return (baseAmount * 1e18) / _exchangeRate;
    }

    function ltToBaseAmount(
        uint256 ltAmount
    ) public view returns (uint256) {
        return (ltAmount * _exchangeRate) / 1e18;
    }
```

**File:** packages/contracts/src/Zap.sol (L323-325)
```text
        } else {
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
            uint256 ltUntilGraduation = $.bonding.previewLtUntilGraduation(tokenAddress);
```

**File:** packages/contracts/src/Zap.sol (L359-360)
```text
            $.usdc.forceApprove(lt, baseToConvert);
            ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
```

**File:** packages/contracts/src/Bonding.sol (L719-726)
```text
        uint256 ltUntilThreshold = type(uint256).max;
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }
```
