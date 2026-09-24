### Title
Hardcoded `/1e12` decimal-scaling assumption in `Zap._sellInternal`'s dust-guard bricks sells if USDC decimals ≠ 6 - (File: `packages/contracts/src/Zap.sol`)

### Summary
`Zap._sellInternal` computes a curve-sell dust-guard by scaling an 18-dp LT-rate estimate down to "USDC precision" with a hardcoded `/1e12` divisor, exactly the same class of bug as the referenced report (hardcoded assumption that USDC has 6 decimals). [1](#0-0) 

### Finding Description
`_sellInternal` estimates the gross USDC value of a curve sell from the LT's 18-dp `exchangeRate()`, then unconditionally divides by `1e12` to compare against `minUsdcAmount()`:
```solidity
uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();
``` [1](#0-0) 

This is documented as a deliberate decimal-normalisation for a "6-dp `minUsdcAmount`" against an "18-dp gross USD estimate," and the test suite treats the `/1e12` divisor as the fix for a prior regression: [2](#0-1) 

`minUsdcAmount()` is sourced live from BounceTech's `GlobalStorage.minTransactionSize()`, which is denominated in the *native* decimals of whatever USDC token BounceTech's LT actually settles in on that chain, not a fixed 6-dp value: [3](#0-2) 

The `USDC` address itself is a single hardcoded constant baked into the deploy script for one target chain (HyperEVM mainnet), with no on-chain `decimals()` read or dynamic scaling factor anywhere in `Zap`, `Bonding`, or the `IBounceLeveragedToken` interface: [4](#0-3) [5](#0-4) 

Exactly as in the M-4 report, the `1e12` scaling factor is a hardcoded assumption (`18dp estimate → 6dp compare`) rather than a value derived from `IERC20Metadata(usdc).decimals()`. If the deployed/configured reserve USDC ever has a decimal count other than 6 (whether from a redeploy to a different chain, or BounceTech migrating its underlying settlement asset), `minUsdcAmount()` would be expressed in that token's native decimals while `grossUsdcEstimate/1e12` remains hardwired to a 6-dp assumption, permanently desynchronising the two sides of the comparison.

### Impact Explanation
If USDC decimals ≠ 6 on the deployed/target chain:
- `minUsdcAmount()` (native decimals, e.g. 18-dp) becomes orders of magnitude larger than `grossUsdcEstimate/1e12` for any real-world sell size, so the guard at [6](#0-5)  reverts on essentially every legitimate curve sell.
- Because `Zap.sell` has no fallback path for pre-graduation curve sells (only `_sellOnCurve` or, post-graduation, `_sellOnUniswapV2`), this permanently bricks the sell side of the AMM for every trader, functionally freezing their ability to exit curve positions through the only sanctioned unprivileged sell path (`Zap.sell`, whitelisted in scope). Holders would be stuck holding tokens with no working exit until graduation (and even then only if `canGraduate` conditions happen to be met independently of a sell attempt).
- This matches the "permanent freezing of trader funds" impact bar, mirroring the systemic, deterministic nature of the M-4 report (no attacker required — it fires automatically for any sell once the mismatch condition holds).

### Likelihood Explanation
Likelihood is tied entirely to whether the reserve USDC's decimals ever diverge from 6 — the current hardcoded `Deploy.s.sol` USDC address is fixed for HyperEVM mainnet, so under the *current* single deployment this exact byte-for-byte failure mode is latent rather than actively triggered. However, per the "Reject... bugs inside BounceTech LT... themselves" and "no-impact analogs" scope rules, this must stand on alt.fun's own code: the root cause — a hardcoded `1e12` decimal-scaling constant instead of a `decimals()`-derived factor — is present in `Zap.sol` today, identical in class and mechanism to the audited M-4 finding, and would activate deterministically (no attacker action needed) the moment the assumption is violated (redeploy to a different chain/USDC, or an underlying settlement-asset migration by BounceTech).

### Recommendation
Replace the hardcoded `/1e12` conversion in `_sellInternal` with a decimals-aware scaling factor derived from the actual USDC token, e.g.:
```solidity
uint8 usdcDecimals = IERC20Metadata(address($.usdc)).decimals();
uint256 grossUsdcEstimate = Math.mulDiv(ltReceived, IBounceLeveragedToken(lt).exchangeRate(), 1e18);
uint256 grossUsdcScaled = usdcDecimals >= 18
    ? grossUsdcEstimate
    : grossUsdcEstimate / (10 ** (18 - usdcDecimals));
if (grossUsdcScaled < minUsdcAmount()) revert BelowMinAmount();
```
Store `usdcDecimals` as an immutable set at `initialize` time (mirroring the mitigation given in the M-4 report) and remove every hardcoded `1e12`/6-dp assumption from `Zap.sol` and its comments.

### Proof of Concept
1. Deploy `Zap` with a mock USDC token configured to 18 decimals (as `DeployHelper.sol` already demonstrates OZ-default 18-dp mock USDC is used in the test suite) and a `MockBounceGlobalStorage.minTransactionSize()` set to a realistic native-decimals floor (e.g. `10e18` for "$10" at 18-dp).
2. Launch a token via `_createToken`, buy a normal-sized position via `zap.buy`.
3. Call `zap.sell(tokenAddr, tokensOut, 0)` for a sell whose `grossUsdcEstimate` (18-dp) is legitimately well above `$10` (e.g. `50e18`).
4. Observe: `grossUsdcEstimate / 1e12` (≈ `5e7`) is compared against `minUsdcAmount()` (`10e18`), so the guard reverts `BelowMinAmount()` even though the sell is 5x the real floor — demonstrating the sell path is permanently bricked whenever USDC decimals ≠ 6, exactly the scaling mismatch class described in the M-4 report. [7](#0-6)

### Citations

**File:** packages/contracts/src/Zap.sol (L444-445)
```text
        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();
```

**File:** packages/contracts/src/Zap.sol (L628-635)
```text
    /// @notice Live BounceTech `mint`/`redeem` floor in USDC (6dp), sourced
    ///         from `GlobalStorage` so a change to their floor is honoured
    ///         without a redeploy. Used as the pre-flight buy/sell minimum
    ///         and as the graduation floor-bump target; also surfaced for
    ///         off-chain callers sizing minimum trades.
    function minUsdcAmount() public view returns (uint256) {
        return _s().bonding.bounceGlobalStorage().minTransactionSize();
    }
```

**File:** packages/contracts/test/Zap.t.sol (L622-645)
```text
    /// @dev Regression for issue #313. The sell-side guard compares an
    ///      18-dp gross USD estimate to the 6-dp `minUsdcAmount`, so it
    ///      must normalise scales before comparing. Without normalisation,
    ///      sells whose 18-dp estimate sits between `1e7` (the raw
    ///      `minUsdcAmount` literal) and `1e19` ($10 in 18dp) bypass the
    ///      guard on mainnet, and the LT then reverts with the undecodable
    ///      `0x05eb05ac` selector instead.
    function test_sell_belowMinAmount_normalisesDecimalScale() public {
        address tokenAddr = _createToken(0);
        uint256 tokensOut = _buyViaRouter(tokenAddr, trader, _smallBuyUsdc());

        // Sell a tiny slice (~0.1% of holdings). At default exchangeRate
        // (1e18 = $1/LT), this yields well under $10 worth of LT. With
        // 18-dp mock USDC, `grossUsdcEstimate` lands in the dead zone the
        // un-normalised guard misses (>> 1e7, but < 1e19). The fix divides
        // by 1e12 first, so the sub-`$10` sell is rejected up front.
        uint256 sellAmount = tokensOut / 1000;

        vm.startPrank(trader);
        Token(tokenAddr).approve(address(zap), sellAmount);
        vm.expectRevert(Zap.BelowMinAmount.selector);
        zap.sell(tokenAddr, sellAmount, 0);
        vm.stopPrank();
    }
```

**File:** packages/contracts/script/Deploy.s.sol (L16-22)
```text
    // HyperEVM mainnet addresses
    address constant USDC = 0xb88339CB7199b77E23DB6E890353E22632Ba630f;
    /// @dev UniswapV2-compatible router (HyperSwap V2 on HyperEVM mainnet).
    address constant UNISWAP_V2_ROUTER = 0xb4a9C4e6Ea8E2191d2FA5B380452a634Fb21240A;
    /// @dev BounceTech `GlobalStorage` (HyperEVM mainnet). Mirrors
    ///      `GLOBAL_STORAGE_ADDRESS` in `bounce-tech/bounce-npm`.
    address constant BOUNCE_GLOBAL_STORAGE = 0xa07d06383c1863c8A54d427aC890643d76cc03ff;
```
