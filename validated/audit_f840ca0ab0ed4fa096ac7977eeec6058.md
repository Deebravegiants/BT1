### Title
Direct token donation to a curve `Pair` permanently disables the overflow-cap buy path and freezes the token's raised LT below graduation - ([File: packages/contracts/src/Router.sol])

### Summary
`Router._computeBuy` caps the last curve buy at the pair's live `tokenBalance()` and back-calculates the LT the trader must pay by computing `cappedReserveToken = reserveToken - tokensOut`. This subtraction assumes the "virtual-reserve invariant" documented in `test/GraduationInvariants.t.sol` (`tokenBalance() < reserve0` always holds), but that invariant is only maintained through the curve's own `swap()` accounting — it is never enforced against a plain ERC20 `transfer` of the launched `Token` directly into the `Pair` contract. An unprivileged holder who accumulates ≥ `LP_RESERVE` (250M) tokens and donates them straight to the `Pair` can permanently collapse the 250M gap between the stored virtual `tokenReserve` and the live `tokenBalance()`, causing every future buy that would exhaust the curve to revert (`OverflowCapDegenerate`) or Panic-underflow, with no way to reverse the donation.

### Finding Description
`Router._computeBuy` computes the capped path as: [1](#0-0) 

`reserveToken` (`_pool.tokenReserve`) is mutated only by `Pair.swap`, which decrements it by exactly the tokens sold on each buy, while `Pair.transferToken` moves the same amount out of the pair's real ERC20 balance — so under normal trading the gap `reserveToken - tokenBalance()` is a constant `LP_RESERVE = 250M`, as asserted by `test_inv_virtualReserveAlwaysExceedsRealBalance`: [2](#0-1) 

However, `Pair.tokenBalance()` is a raw `balanceOf` read, and nothing in `Pair.sol` gates who can transfer the launched `Token` (a standard ERC20 clone) into the pair: [3](#0-2) 

Any address that has previously bought (or otherwise acquired) `D` real tokens off the curve and sends them back to the `Pair` via a plain `transfer` inflates `tokenBalance()` by `D` without changing `_pool.tokenReserve` (only `Pair.swap`/`Router` mutate it). Re-deriving the cap math: because the pre-donation gap is always exactly `LP_RESERVE`, the new gap after a `D`-token donation becomes `LP_RESERVE - D`, independent of which specific buy later triggers the capped branch. Once any future buy's naive `tokensOut` exceeds the (now inflated) `tokenBalance()`, `_computeBuy` recomputes `cappedReserveToken = reserveToken - tokensOut` and, for `D ≥ LP_RESERVE (250M)`, this is `≤ 0` — an arithmetic underflow Panic (or, at the boundary, `revert OverflowCapDegenerate()`), permanently reverting that and every subsequent buy that would need to draw down to the (permanently elevated) real balance.

This breaks the supply-side graduation trigger `IPair.tokenBalance() == 0`, which is exactly the mechanism `canGraduate`/`triggerGraduation` rely on for tokens whose LT never appreciates enough to hit the USD trigger: [4](#0-3) 

Because `Pair` exposes no sweep/burn for donated balance outside of `_prepareGraduationLiquidity` (which only runs once graduation is entered — i.e. once one of the two triggers fires), and the donation itself can never be reversed, a token whose LT price stagnates is left permanently unable to complete its curve: any buy attempting to consume the last real tokens is guaranteed to revert forever, and the LT raised on the curve, plus the curve seed, remains stuck in the `Pair` with no path to `Router.graduate` draining it.

### Impact Explanation
This freezes the curve-raised LT (all buyers' capital funneled into the pair) and the creator's/protocol's future fee stream on that token indefinitely — the token can never reach `Lifecycle.Graduating`/`Graduated` via the supply trigger, and if the LT's `exchangeRate()` never appreciates enough to cross `graduationThresholdUsd`, there is no other path to drain the pair or unlock trading past the crippled tail of the curve. This is a permanent freezing of trader/creator funds reachable by a single unprivileged address, satisfying the Medium-severity bar (analogous to the CVE's own "unexpected invariant violated → assertion/crash" bug class, here manifesting as an unenforced invariant leading to an unrecoverable arithmetic Panic/DoS in `Router._computeBuy`).

### Likelihood Explanation
The attack requires the attacker to first acquire `≥ LP_RESERVE` (250M, i.e., a third of the 750M curve-sellable supply) of the specific launched token via ordinary `Bonding.buy` calls, then send it back to the `Pair` with a plain ERC20 `transfer`. This is capital-intensive but requires no privileged role, no protocol bug beyond the missing donation-invariant check, and no cooperation from `Bonding`/`Zap`/`Router` owners — it is purely a griefing/sabotage vector (e.g., a competitor bricking a rival's launch) rather than a profit-motivated exploit, which keeps likelihood at the lower end of Medium but the finding remains concretely reachable and irreversible once triggered.

### Recommendation
Cap `_computeBuy`'s capped-branch usage of `tokenBalance()` against the pair's own accounted `tokenReserve`/sold-supply bookkeeping rather than trusting the live ERC20 balance directly, or clamp/burn any balance in excess of the expected `reserveToken - LP_RESERVE` amount before it can participate in the cap computation (mirroring the unconditional-burn treatment `_prepareGraduationLiquidity` already applies to donations at graduation time, but performed proactively on every buy instead of only after a trigger fires). At minimum, replace the raw subtraction with a saturating computation and an explicit guard that treats `tokenBalance() >= reserveToken` as "curve already exhausted" rather than letting it underflow or hard-revert the transaction.

### Proof of Concept
1. Launch a token via `Zap.createToken`; curve seeds `Pair` with `reserve0 = totalSupply (1B)`, `tokenBalance() = curveSupply (750M)`, `LP_RESERVE = 250M` held in `Bonding`.
2. Attacker (unprivileged) calls `Zap.buy` repeatedly until they hold `D = 250M` of the launched `Token` (verifiable via `Router.previewBuy`/`getAmountOut` to size the buys); at this point `_pool.tokenReserve = 1B - 250M = 750M`, `tokenBalance() = 750M - 250M = 500M` (gap still `250M`).
3. Attacker calls `Token.transfer(pairAddress, 250_000_000e18)` directly — a plain ERC20 transfer with no special permission — raising `tokenBalance()` to `750M` while `_pool.tokenReserve` stays at `750M` (gap collapses to `0`).
4. Any subsequent trader calls `Zap.buy`/`Bonding.buy` with an amount large enough that `Router._computeBuy`'s naive `tokensOut` exceeds the now-`750M` `tokenBalance()` (i.e., an attempt to buy the remaining real supply, which will eventually happen as the curve is traded down): `tokensOut` is capped to `realBalance = 750M`, then `cappedReserveToken = reserveToken (750M) - tokensOut (750M) = 0` → `revert OverflowCapDegenerate()` (or, if the donation exceeded 250M, a raw arithmetic underflow Panic). This revert is permanent and unrecoverable — the curve can never be fully sold out, `IPair.tokenBalance() == 0` can never be satisfied, and `canGraduate`'s supply trigger is permanently disabled for this token, freezing the pool's raised LT unless/until the (possibly never-reached) USD trigger fires.

### Citations

**File:** packages/contracts/src/Router.sol (L140-147)
```text
        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-377)
```text
    // ─── 8. Virtual reserve invariant (tokenBalance < tokenReserve) ──────

    /// @dev Production seeding (`virtualReserveToken = totalSupply`,
    ///      `realTokenAmount = curveSupply = 75% * totalSupply`) makes
    ///      `pair.tokenBalance() < pair.tokenReserve()` a hard property at
    ///      every state of the curve. This invariant is what makes the
    ///      `cappedReserveToken == 0` branch in `Router._computeBuy`
    ///      unreachable; if it ever ceased to hold, that branch would
    ///      revert with `OverflowCapDegenerate` rather than over-pay.
    function test_inv_virtualReserveAlwaysExceedsRealBalance() public {
        (address tokenAddr, address pairAddr) = _launchNoSeed();

        // Right after launch.
        assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "post-launch invariant");

        // After a series of buys the property must continue to hold while
        // the curve is still trading.
        for (uint256 i = 0; i < 10; i++) {
            if (!bonding.isTrading(tokenAddr)) break;
            _buy(tokenAddr, trader, 100 ether);
            if (bonding.isTrading(tokenAddr)) {
                assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "invariant must hold after every buy");
            }
        }
    }
```

**File:** packages/contracts/src/Pair.sol (L103-105)
```text
    function tokenBalance() external view returns (uint256) {
        return IERC20(launchedToken).balanceOf(address(this));
    }
```

**File:** packages/contracts/src/Bonding.sol (L680-695)
```text
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```
