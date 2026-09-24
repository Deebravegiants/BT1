## Title
Missing lower-bound check on `virtualLtReserve` lets a creator launch a curve with `k = 0`, letting the first buyer drain the entire curve supply for ~0 payment - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._deployAndSeed` derives the curve's virtual LT reserve from a live, externally-controlled `exchangeRate()` and only bounds it from above. There is no check that `virtualLtReserve` is non-zero, so a sufficiently high `exchangeRate()` on any BounceTech-registered LT rounds `virtualLtReserve` down to `0`, setting the pair's `k = totalSupply * 0 = 0`. Against a `k = 0` curve, `Router._computeBuy`'s overflow-cap back-calculation resolves `amountInUsed = 0` while `tokensOut` is capped at the pair's full real balance (the 750M curve supply) — i.e., the first buyer receives the whole curve supply for free.

### Finding Description
`Bonding._deployAndSeed` computes:
```solidity
uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
if (exchangeRate == 0) revert ZeroExchangeRate();
uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();
...
$.router.addInitialLiquidity(tokenAddr, totalSupply, curveSupply, virtualLtReserve);
``` [1](#0-0) 

Only an *upper* bound on `virtualLtReserve` is enforced (`ExchangeRateTooLow`, guarding the `uint112` HyperSwap reserve slot). There is no lower bound guarding against `virtualLtReserve` rounding to `0` when `exchangeRate` is very large relative to `VIRTUAL_LIQUIDITY_USD * 1e18`. `Router.addInitialLiquidity` then calls `IPair(pairAddr).mint(virtualReserveToken, reserveAsset)` with `reserveAsset = 0`, which — per the natspec — permanently fixes `k = tokenReserve * assetReserve = totalSupply * 0 = 0`, and `Pair.swap` never modifies `k` afterward: [2](#0-1) 

With `k = 0`, `Router._computeBuy` degenerates:
```solidity
uint256 newReserveAsset = reserveAsset + amountInUsed;
tokensOut = reserveToken - (k / newReserveAsset);   // = reserveToken - 0
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;                         // capped at curveSupply (750M)
    uint256 cappedReserveToken = reserveToken - tokensOut;  // = LP_RESERVE (250M), nonzero — no revert
    uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken; // = 0 (k=0)
    amountInUsed = cappedReserveAsset - reserveAsset; // = 0 - 0 = 0
}
``` [3](#0-2) 

So for any buy against this curve, `tokensOut` is forced to the entire real curve-supply balance while `amountInUsed` computes to `0`. The `OverflowCapDegenerate` guard only fires when `cappedReserveToken == 0`; here it is `LP_RESERVE` (250M tokens), which is non-zero, so the revert never triggers. `Router.buy` then does `IERC20(asset).safeTransferFrom(to, pairAddr, 0)` (a no-op) and transfers the full 750M-token curve supply to the caller.

This is directly analogous to the reported `Cooler.collateralFor()` issue: an attacker-reachable parameter feeding a division causes the required payment to round to `0` while the payout proceeds in full. Here the "attacker-chosen ratio" is the choice of a BounceTech-registered LT whose live `exchangeRate()` is high enough (any unprivileged wallet can call `Zap.createToken`/`Bonding.launch` naming any BounceTech-registered `ltAddress`), and the missing check is a lower bound on `virtualLtReserve` (equivalently, a floor on `exchangeRate` derived from `VIRTUAL_LIQUIDITY_USD`), mirroring the missing floor on `loanToCollateral_` in the original report.

Note: the `launch` path does gate `ltAddress` against BounceTech's live LT-existence registry (`UnknownLeveragedToken`), but that gate only checks *registration*, not `exchangeRate` magnitude — so any registered LT whose price has drifted (or is set) high enough is a valid, reachable vector. [4](#0-3) 

### Impact Explanation
Whoever performs the first buy against a degenerate `k=0` curve (this could be the launching creator's own mandatory seed buy via `Zap.createToken`, or any subsequent trader) receives the entire 750M-token curve supply for `amountInUsed = 0` LT. Because the curve's real balance immediately drains to zero, the supply-based graduation trigger (`tokenBalance() == 0`) fires on the very same transaction, permanently locking in the state and pushing the token to graduation with `ltFromPair = storedAssetReserve - virtualLtReserve = 0`, i.e., essentially no LT ever backs the LP. The attacker walks away holding 750M tokens acquired for free, which they can immediately dump on the post-graduation HyperSwap pool for real USDC/LT extracted from later buyers/LPs — concrete theft of value from every future participant and an unbacked token payout, matching the "Accept only concrete theft... unbacked token or LT payouts" validation criterion.

### Likelihood Explanation
Reachability requires only that some BounceTech-registered LT have (or later drift to) an `exchangeRate()` large enough that `(VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate == 0`. `VIRTUAL_LIQUIDITY_USD` is a small fixed constant (opening curve depth ~ thousands of USD), while BounceTech LTs are leveraged, rebasing instruments whose `exchangeRate` can legitimately grow by orders of magnitude over their lifetime (that's the entire point of a leveraged token). Any unprivileged wallet can call `Bonding.launch`/`Zap.createToken` naming any currently-registered LT as `ltAddress` — this is a normal, permissionless, unprivileged action, requiring no special timing, front-running, or governance/oracle compromise. This is the same design class the code already defends against on the *other* side (`ExchangeRateTooLow` for the uint112 overflow bound) — the missing complementary lower-bound check is a straightforward oversight rather than a hypothetical edge case.

### Recommendation
Add an explicit lower-bound revert in `Bonding._deployAndSeed` immediately after computing `virtualLtReserve`, e.g.:
```solidity
if (virtualLtReserve == 0) revert ExchangeRateTooHigh();
```
or better, enforce a meaningful minimum (e.g., require `virtualLtReserve >= curveSupply / MAX_ALLOWED_PRICE_RATIO` or some floor tied to precision) so that `k` can never be degenerate. Additionally, `Router._computeBuy`'s `OverflowCapDegenerate` check should be extended to also guard `cappedReserveAsset == reserveAsset` (i.e., `amountInUsed == 0`) as a defense-in-depth invariant, since a zero-cost buy against any positive `tokensOut` should never be allowed to succeed regardless of how the degenerate reserve state arose.

### Proof of Concept
1. An unprivileged wallet calls `Zap.createToken(...)` / `Bonding.launch(...)` with `ltAddress` set to a BounceTech-registered LT whose `exchangeRate()` satisfies `exchangeRate > VIRTUAL_LIQUIDITY_USD * 1e18` (e.g., a long-lived leveraged LT that has rebased to a high price, or one deliberately deployed/registered at a high starting price).
2. `_deployAndSeed` computes `virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate = 0` (integer division rounds down) — no revert fires because only the upper bound (`ExchangeRateTooLow`) is checked. [5](#0-4) 
3. `Router.addInitialLiquidity` mints the pair with `reserveAsset = 0`, fixing `k = totalSupply * 0 = 0` for the life of the pair. [6](#0-5) 
4. The mandatory seed buy (or any subsequent `Zap.buy`) triggers `Router.buy` → `_computeBuy`. With `k = 0`, the overflow-cap path computes `cappedReserveAsset = 0` and thus `amountInUsed = 0`, while `tokensOut` is set to the full real balance of the curve supply (750M tokens). [7](#0-6) 
5. `IERC20(asset).safeTransferFrom(to, pairAddr, 0)` is a no-op; `IPair(pairAddr).transferToken(to, tokensOut)` sends the buyer the entire 750M curve supply. The trade costs the buyer nothing in LT.
6. The curve's real token balance is now `0`, immediately satisfying the supply-based graduation trigger, and the attacker holds free tokens to sell on the graduated market.

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-494)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();

        IERC20(tokenAddr).forceApprove(address($.router), curveSupply);
        // Virtual tokenReserve = full totalSupply; only curveSupply (75%) actually transferred.
        // The launch-time `virtualLtReserve` is recoverable later as
        // `Pair.k() / Token.TOTAL_SUPPLY()`: `Pair.mint` sets `_pool.k =
        // tokenReserve * assetReserve = totalSupply * virtualLtReserve` once
        // and `Pair.swap` never modifies `_pool.k`. That identity is what
        // `_launchTimeVirtualLtReserve` exploits to derive donation-immune
        // raised-LT in `canGraduate` and `_prepareGraduationLiquidity`.
        $.router.addInitialLiquidity(tokenAddr, totalSupply, curveSupply, virtualLtReserve);
```

**File:** packages/contracts/src/Router.sol (L75-87)
```text
    function addInitialLiquidity(
        address token,
        uint256 virtualReserveToken,
        uint256 realTokenAmount,
        uint256 reserveAsset
    ) external onlyRole(BONDING_ROLE) {
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();

        IERC20(token).safeTransferFrom(msg.sender, pairAddr, realTokenAmount);
        IPair(pairAddr).mint(virtualReserveToken, reserveAsset);
    }
```

**File:** packages/contracts/src/Router.sol (L127-148)
```text
    function _computeBuy(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 amountInUsed, uint256 tokensOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        amountInUsed = amountIn;

        uint256 newReserveAsset = reserveAsset + amountInUsed;
        tokensOut = reserveToken - (k / newReserveAsset);

        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
    }
```

**File:** packages/contracts/test/BounceFactoryGate.t.sol (L46-66)
```text

    function test_launch_succeedsForRegisteredLT() public {
        // `_deployCore` registers the default mock LT in the factory, so the
        // standard launch path should pass the gate.
        Bonding.LaunchParams memory params = _launchParams(address(lt));
        vm.prank(creator);
        (address tokenAddr,) = bonding.launch(params, creator);
        assertTrue(tokenAddr != address(0));
    }

    function test_launch_revertsOnUnregisteredLT() public {
        // Brand-new LT that exists on-chain but was never registered with
        // BounceTech — exactly the malicious-LT case described in the issue.
        MockLeveragedToken rogueLT =
            new MockLeveragedToken("Rogue", "ROGUE", LT_EXCHANGE_RATE, 2, true, "ROGUE", address(usdc));

        Bonding.LaunchParams memory params = _launchParams(address(rogueLT));
        vm.prank(creator);
        vm.expectRevert(abi.encodeWithSelector(Bonding.UnknownLeveragedToken.selector, address(rogueLT)));
        bonding.launch(params, creator);
    }
```
