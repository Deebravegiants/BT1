### Title
Rounding-up-in-favor-of-seller in `Router._computeSell` can permanently freeze the last seller's exit from the curve - ([File: packages/contracts/src/Router.sol])

### Summary
`Router._computeSell` computes the LT payout for a sell by floor-dividing `k / newReserveToken` and subtracting the result from `reserveAsset`. Because integer division truncates, this subtraction always rounds `assetOut` **up** in favor of the seller (mirroring the Napier `Tranche._computePrincipalTokenRedeemed` rounding-down-in-favor-of-user bug class, which produced insufficient burn/backing for the last redeemer). Unlike `Router.buy`, which explicitly caps `tokensOut` at the pair's real `tokenBalance()` to protect against exactly this class of overpayment, `Router.sell` has **no analogous cap against the pair's real LT balance** before calling `IPair.transferAsset`.

### Finding Description
`Pair.sol`'s bonding-curve reserve accounting is virtual on the LT (asset) side: at launch only `curveSupply` (750M) of tokens are transferred as real balance, while `reserve0`/`tokenReserve` is seeded at the full `totalSupply` (1B); analogously, `assetReserve` starts at a virtual `virtualLtReserve` value with zero real LT actually held by the pair [1](#0-0) . The real LT balance held by the `Pair` at any time is exactly `reserveAsset - virtualLtReserve` — this is only an exact invariant if every subtraction/transfer of `assetOut` from `reserveAsset` is matched to a real ERC20 transfer of the same size.

`Router._computeSell` computes the seller's payout as:
```solidity
uint256 newReserveToken = reserveToken + amountIn;
assetOut = reserveAsset - (k / newReserveToken);
``` [2](#0-1) 

`k / newReserveToken` floors, so the subtracted term is rounded down, meaning `assetOut` is rounded **up** — the seller receives up to 1 wei more LT than the exact constant-product price implies, on every single sell. This is explicitly acknowledged by the project's own fuzz test:
```solidity
function testFuzz_buyThenSell_noProfit(uint256 buyAmount) public {
    ...
    assertTrue(assetOut <= buyAmount + 1, "Should never profit on round trip (rounding only)");
}
``` [3](#0-2) 

Critically, `Router.sell` calls `IPair.transferAsset(to, assetOut)` **before** calling `IPair.swap(...)`, and never checks `assetOut` against the pair's real, physically-held LT balance:
```solidity
function sell(uint256 amountIn, address token, address to) external onlyRole(BONDING_ROLE) returns (uint256 tokensIn, uint256 assetOut) {
    ...
    IERC20(token).safeTransferFrom(to, pairAddr, amountIn);
    assetOut = _computeSell(pairAddr, amountIn);
    IPair(pairAddr).transferAsset(to, assetOut);
    IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
}
``` [4](#0-3) 

By contrast, `Router.buy` explicitly guards the symmetric case — a rounding-up of `tokensOut` that could exceed the pair's real `tokenBalance()` — with an overflow cap that back-calculates the LT actually charged:
```solidity
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;
    ...
}
``` [5](#0-4) 

No equivalent cap exists on the sell side to protect the real LT balance (`reserveAsset - virtualLtReserve`) that the pair actually holds. If accumulated per-sell 1-wei rounding pushes the required `assetOut` on a subsequent sell above the pair's remaining real LT balance (which shrinks toward zero as the curve is drained by sells, or is naturally small right after buys where `amountInUsed` is tightly capped by the overflow-buy path), the `IERC20(assetToken).safeTransfer` inside `Pair.transferAsset` will revert with "ERC20: transfer amount exceeds balance" — exactly the failure mode described in the Napier report, where the last quitter's transaction reverts and their position becomes stuck. Since `Pair.swap`'s K-invariant check (`(newTokenReserve+1)*(newAssetReserve+1) < k`) is evaluated on the virtual accounting numbers, not the real balance, the swap itself would not reject the trade before the real-balance-insufficient transfer already reverted — the seller cannot resubmit a smaller trade that still nets a full exit, and if they hold the last remaining real tokens on the curve, they are permanently unable to sell/exit that position through the curve.

### Impact Explanation
This is a fund-freezing bug reachable by any unprivileged trader calling `Zap.sell` → `Bonding.sell` → `Router.sell`, no privileged role required. A seller (particularly the last seller draining the curve, or any seller landing on a reserve state where accumulated rounding has eaten into the real/virtual buffer) can have their sell transaction unconditionally revert, permanently preventing them from exiting their token position through the curve (their only other option, waiting for graduation, may never occur if the curve never reaches the graduation threshold). This matches the "permanent freezing of trader funds" acceptance criterion.

### Likelihood Explanation
The rounding error per sell is bounded at 1 wei of LT (18-decimals), so triggering an outright revert requires the pair's real remaining LT buffer to be driven down to a similarly small residual — which happens naturally as the curve is drained toward the supply-trigger graduation boundary (`tokenBalance() == 0`), or after many trades accumulate the 1-wei-per-trade drift. This is a low-magnitude-per-event but architecturally present bug: there is no explicit cap protecting the real asset balance on the sell path, unlike the symmetric protection that exists on the buy path. Likelihood is elevated by the fact that curves are specifically designed to be drained close to zero real token/LT balance as part of normal, expected operation (the supply-trigger graduation path), which is exactly the regime where this rounding gap becomes exploitable/triggerable.

### Recommendation
Round `_computeSell`'s output down (in favor of the protocol/pair) rather than up, mirroring the Napier fix of switching `mulWadDown` to `mulWadUp` in the opposite direction:
```solidity
function _computeSell(address pairAddr, uint256 amountIn) internal view returns (uint256 assetOut) {
    IPair pair = IPair(pairAddr);
    (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
    uint256 k = pair.k();
    uint256 newReserveToken = reserveToken + amountIn;
    // Round the subtracted term up so assetOut rounds down (favor protocol).
    uint256 newReserveAsset = (k + newReserveToken - 1) / newReserveToken;
    assetOut = reserveAsset - newReserveAsset;
}
```
Additionally, add an explicit cap in `Router.sell` (symmetric to `Router.buy`'s `realBalance` cap) that clamps `assetOut` to `IPair(pairAddr).assetBalance() - <virtual reserve floor>` before calling `transferAsset`, so a sell can never request more real LT than the pair physically holds, guaranteeing the transaction always succeeds rather than reverting on the last exit.

### Proof of Concept
Exact reproduction requires driving the pair's real LT balance down to a residual comparable to the accumulated 1-wei-per-sell rounding drift (e.g., via many small sells or via the overflow-buy cap path that intentionally minimizes `amountInUsed`, followed by a sell that computes `assetOut` exceeding the remaining real balance) and asserting that `Router.sell`/`IPair.transferAsset` reverts with `ERC20: transfer amount exceeds balance`. I was not able to fully execute or verify a concrete numeric trace within the available tool budget (no terminal/test-runner access), so this should be validated with a Foundry test analogous to `testFuzz_buyThenSell_noProfit` in `packages/contracts/test/Router.t.sol`, driving cumulative sells until the pair's real `assetBalance()` is exhausted and confirming the final sell reverts rather than succeeding.

### Citations

**File:** packages/contracts/src/Router.sol (L71-87)
```text
    /// @param virtualReserveToken Token reserve stored in the pair (defines K);
    ///                            may exceed `realTokenAmount`.
    /// @param realTokenAmount    Tokens actually transferred (sellable supply).
    /// @param reserveAsset       Virtual LT reserve (no real LT moved here).
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

**File:** packages/contracts/src/Router.sol (L151-170)
```text
    function sell(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 tokensIn, uint256 assetOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        tokensIn = amountIn;

        IERC20(token).safeTransferFrom(to, pairAddr, amountIn);

        assetOut = _computeSell(pairAddr, amountIn);

        IPair(pairAddr).transferAsset(to, assetOut);

        IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
    }
```

**File:** packages/contracts/src/Router.sol (L172-182)
```text
    function _computeSell(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 assetOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        uint256 newReserveToken = reserveToken + amountIn;
        assetOut = reserveAsset - (k / newReserveToken);
    }
```

**File:** packages/contracts/test/Router.t.sol (L402-409)
```text
    function testFuzz_buyThenSell_noProfit(
        uint256 buyAmount
    ) public {
        buyAmount = bound(buyAmount, 1 ether, 3000 ether);
        uint256 tokensOut = _doBuy(trader, buyAmount);
        uint256 assetOut = _doSell(trader, tokensOut);
        assertTrue(assetOut <= buyAmount + 1, "Should never profit on round trip (rounding only)");
    }
```
