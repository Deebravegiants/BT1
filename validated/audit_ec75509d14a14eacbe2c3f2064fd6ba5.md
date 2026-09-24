### Title
Rebalance-swap rounding-to-zero forces a large hostile pre-seed into the unguarded `_seedDirectMint` path, letting the LP be seeded away from the curve-close price - (File: `packages/contracts/src/Bonding.sol`)

### Summary
CVE-2018-19824's root cause is a degenerate edge case (a USB device reporting **zero** interfaces) that the ALSA probe path never validates before continuing to operate on the (empty) structure, corrupting later processing. `Bonding._seedRebalancing` has the same shape of bug: it treats "the corrective rebalance swap computed to **zero**" (`_pairRebalance` returning `false`) as proof that the hostile pre-seed reserves are *negligible*, and unconditionally falls back to `_seedDirectMint` — a mint path that is only safe against small reserves. That assumption is false: a swap can round to zero against **arbitrarily large** pre-seeded reserves whenever the attacker's ratio is already extremely close to (but not exactly) the curve-close ratio, because `_noFeeSwapInput`'s integer `sqrt` truncates sub-wei deltas regardless of the reserves' absolute magnitude.

### Finding Description
`_seedRebalancing` handles a "mint pre-seed" (regime 3: attacker already minted LP against a self-chosen `(reserveToken, reserveLT)`): [1](#0-0) 

When the pool is off-ratio it calls `_pairRebalance`, and if that returns `false` it falls straight into `_seedDirectMint`: [2](#0-1) 

`_pairRebalance` returns `false` whenever the no-fee swap size `s` rounds to `0`, or the fee-charging quote on that `s` rounds to `0`: [3](#0-2) 

`s = sqrt(reserveIn * reserveOut * targetN / targetD) - reserveIn`. This is an **integer** square-root; whenever the attacker's chosen `(reserveToken, reserveLT)` sits extremely close to the curve-close ratio `tokensForLP/ltFromPair` — a ratio the attacker can hit to sub-wei precision because they fully control both reserves up to the `uint112` ceiling — `sqrt(product)` truncates to `<= reserveIn` and `s` collapses to `0`, even though `reserveToken`/`reserveLT` themselves are enormous (up to `type(uint112).max`).

The code's own comment asserts the opposite is guaranteed: [4](#0-3) 
"the reserves are then negligible against this graduation's inventory" — but nothing enforces that; the fallback is reachable at any pre-seed magnitude, not just dust.

Once `_seedDirectMint` fires against a pool that already has non-zero `totalSupply()` (attacker's existing LP), it simply transfers `(tokensForLP, ltFromPair)` to the pair and calls the pair's own `mint(lpLock)`: [5](#0-4) 

Standard V2 `mint()` (in the pre-existing-LP branch) computes `liquidity = min(amount0 * supply / reserve0, amount1 * supply / reserve1)` and — because the deposited amounts are keyed to the curve-close ratio rather than the (attacker-chosen, near-but-not-exact) pool ratio — the disadvantaged side's excess is absorbed as extra reserves that inflate the value of the attacker's pre-existing LP shares rather than the freshly minted (and immediately `LPLock`-ed) shares. Because `LPLock.recordLock` is a one-shot, no-rescue lock, this mis-priced LP position is then permanently sealed with no remediation path: [6](#0-5) 

### Impact Explanation
An attacker who front-runs graduation by creating the HyperSwap V2 pair and self-minting LP at a ratio engineered to be within sub-wei rounding distance of the eventual curve-close ratio forces `finalizeGraduation` to take the `_seedDirectMint` fallback against large, non-negligible reserves. The resulting LP — permanently locked via `LPLock` on behalf of the protocol/token holders — opens at a price skewed by the attacker's crafted reserves, and value that should have accrued to the protocol-owned locked LP is instead captured by the attacker's pre-existing LP shares. This is a concrete "LP seeded away from the curve close price" outcome that permanently disadvantages the token's locked liquidity (traders/LPs), satisfying the Validate criteria for impact. Severity is High given the funds affected (the entire `tokensForLP`/`ltFromPair` deposit, up to `LP_RESERVE` = 250M tokens plus all curve-raised LT) and the permanence of the LPLock sealing.

### Likelihood Explanation
The attacker needs only: (1) permissionlessly create/pre-mint the HyperSwap V2 `TOKEN/LT` pair before `finalizeGraduation` runs (explicitly named as a reachable action in scope), and (2) choose `(reserveToken, reserveLT)` values that land within integer-sqrt rounding distance of the *known* target ratio `tokensForLP/ltFromPair` — a ratio that is deterministically derivable from the curve's public state (`Pair.getReserves()`, `Pair.k()`, `Token.TOTAL_SUPPLY()`) once phase 1 (`_enterGraduating`) has cached it, since `_prepareGraduationLiquidity` never depends on the live `exchangeRate()`. Because the target is fixed and public before phase 2 executes, and `sqrt` truncation only requires being off by a sub-wei fractional amount relative to arbitrarily large reserves (well within `uint112`), this is realistically achievable by any sophisticated actor, not merely a theoretical edge case.

### Recommendation
Do not treat `_pairRebalance() == false` as proof that reserves are negligible. Before falling back to `_seedDirectMint` in the regime-3 branch, explicitly check that `reserveToken`/`reserveLT` are within the same `DIRECT_MINT_PRESEED_BPS` band already used to gate the fast path at the top of `_seedRebalancing` (or a similarly bounded threshold), rather than inferring negligibility from a swap-rounding side effect. If the reserves exceed that band but `_pairRebalance` still cannot execute a corrective swap, revert instead of silently minting into a large, off-ratio, pre-existing LP position.

### Proof of Concept
1. Attacker calls `Bonding._ensureUniswapV2Pair`-equivalent (`IUniswapV2Factory.createPair(token, lt)`) directly against HyperSwap V2 before the token graduates, or simply waits for `TokenGraduating` to know `pendingGraduation[token]` (`tokensForLP`, `ltFromPair`) is fixed.
2. Attacker acquires enough TOKEN (via curve buys, bounded by curve rules) and LT and calls `pair.mint(attacker)` directly with `(reserveToken, reserveLT)` chosen so that `reserveToken/reserveLT` is within a few parts of `2^-256` (i.e., sub-wei after `Math.sqrt`) of `tokensForLP/ltFromPair`, while both reserves are large (near `uint112` max) — feasible offline since both `tokensForLP`/`ltFromPair` are public curve-derived values.
3. Anyone calls `Bonding.finalizeGraduation(token)`. `_seedRebalancing` detects an off-ratio pool, calls `_pairRebalance`, whose `_noFeeSwapInput` truncates `s` to `0` due to the crafted near-exact ratio; `_pairRebalance` returns `false`.
4. `_seedRebalancing` falls back to `_seedDirectMint`, transferring `(tokensForLP, ltFromPair)` into the pair and calling `pair.mint(lpLock)` against the attacker's large existing reserves; V2's `min()` formula donates the mismatched side to the attacker's pre-existing LP shares.
5. `LPLock.recordLock` seals the resulting (mispriced) LP permanently; the attacker can now `pair.burn()` their inflated LP share to extract the donated value, while the protocol-owned locked LP is permanently short-changed.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1168-1176)
```text
    ///           When the seed is small enough that the fee-charging swap
    ///           quote rounds to zero, no swap can move the ratio — but the
    ///           reserves are then negligible against this graduation's
    ///           inventory, so we fall back to the regime-1 direct mint
    ///           (`_seedDirectMint`) and open at the cached ratio anyway.
    ///           The captured LP share is bounded by
    ///           `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`,
    ///           which vanishes for any seed that small.
    ///
```

**File:** packages/contracts/src/Bonding.sol (L1245-1259)
```text
    function _seedDirectMint(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair
    ) internal returns (uint256 liquidity) {
        IERC20(tokenAddress).safeTransfer(pair, tokensForLP);
        IERC20(lt).safeTransfer(pair, ltFromPair);
        liquidity = IUniswapV2Pair(pair).mint(_s().lpLock);
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1316-1349)
```text
        if (reserveToken * ltFromPair > reserveLT * tokensForLP) {
            // Pool TOKEN-rich. tokenIn = lt, tokenOut = tokenAddress.
            // tokenInIs0 = (lt is token0) = !tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: lt,
                        tokenInIs0: !tokenIs0,
                        reserveIn: reserveLT,
                        reserveOut: reserveToken,
                        targetN: ltFromPair,
                        targetD: tokensForLP,
                        maxSwap: _swapBudget(_ltSwapInventory(lt, protectedLT))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        } else if (reserveToken * ltFromPair < reserveLT * tokensForLP) {
            // Pool LT-rich. tokenIn = tokenAddress, tokenInIs0 = tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: tokenAddress,
                        tokenInIs0: tokenIs0,
                        reserveIn: reserveToken,
                        reserveOut: reserveLT,
                        targetN: tokensForLP,
                        targetD: ltFromPair,
                        maxSwap: _swapBudget(IERC20(tokenAddress).balanceOf(address(this)))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        }
```

**File:** packages/contracts/src/Bonding.sol (L1414-1429)
```text
    function _pairRebalance(
        RebalanceParams memory p
    ) internal returns (bool) {
        uint256 s = _noFeeSwapInput(p.reserveIn, p.reserveOut, p.targetN, p.targetD, p.maxSwap);
        if (s == 0) return false;

        // Quote from the pair so the output tracks its live fee; a value
        // derived from a stale fee rate would trip the pair's K-check.
        uint256 expectedOut = IUniswapV2Pair(p.pair).getAmountOut(s, p.tokenIn);
        if (expectedOut == 0) return false;

        IERC20(p.tokenIn).safeTransfer(p.pair, s);
        (uint256 amount0Out, uint256 amount1Out) = p.tokenInIs0 ? (uint256(0), expectedOut) : (expectedOut, uint256(0));
        IUniswapV2Pair(p.pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
        return true;
    }
```

**File:** packages/contracts/src/Bonding.sol (L1507-1522)
```text
    function _noFeeSwapInput(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 targetN,
        uint256 targetD,
        uint256 maxSwap
    ) internal pure returns (uint256) {
        if (reserveIn == 0 || reserveOut == 0 || targetN == 0 || targetD == 0 || maxSwap == 0) {
            return 0;
        }
        uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
        uint256 newIn = Math.sqrt(product);
        if (newIn <= reserveIn) return 0;
        uint256 s = newIn - reserveIn;
        return s > maxSwap ? maxSwap : s;
    }
```

**File:** packages/contracts/src/LPLock.sol (L69-85)
```text
    /// @notice Record an LP lock. LP tokens must already sit at this address.
    function recordLock(
        address token,
        address lpPair,
        uint256 amount
    ) external {
        LPLockStorage storage $ = _s();
        if (!$.isLocker[msg.sender]) revert NotAuthorized();
        if (lpPair == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        // `lockedAt` is the one-shot sentinel: it is always set to a non-zero
        // timestamp on the first lock, so the guard holds for any `amount`.
        if ($.locks[token].lockedAt != 0) revert AlreadyLocked();
        if (IERC20(lpPair).balanceOf(address(this)) < amount) revert InsufficientLPBalance();
        $.locks[token] = LockInfo({lpPair: lpPair, amount: amount, lockedAt: block.timestamp});
        emit LPLocked(token, lpPair, amount);
    }
```
