### Title
Permissionless HyperSwap pre-seed can deterministically brick `finalizeGraduation`, permanently freezing curve-raised LT and 250M tokens on `Bonding` - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding`'s graduation is split across two independently-committed transactions: phase 1 (`_enterGraduating`) permanently drains the curve's raised LT out of the `Pair` via `Router.graduate`, burns unsold/excess tokens, flips `TokenInfo.lifecycle` to `Graduating`, and caches `PendingGraduation`; phase 2 (`finalizeGraduation`) is a *separate*, permissionless transaction that must later seed the HyperSwap V2 LP and call `LPLock.recordLock`. There is no code path that ever reverts the token back to `Lifecycle.Curve` or otherwise reclaims the already-drained LT/tokens if phase 2 cannot succeed. An attacker who permissionlessly pre-creates the token/LT HyperSwap pair and seeds it with an adversarial ratio can push the phase-2 seeding logic into a state where the eventual `pair.mint()` call (or `LPLock.recordLock`'s `amount == 0` guard) deterministically reverts on every retry, since the pathological pair reserves and the frozen `pendingGraduation` values never change. The token is left permanently stuck in `Lifecycle.Graduating` with its LT and 250M `tokensForLP`/curve tokens locked inside `Bonding` forever.

### Finding Description
Phase 1 (`_enterGraduating` → `_prepareGraduationLiquidity`) is inline in the threshold-crossing buy or `triggerGraduation`, and unconditionally:
- burns unsold curve tokens,
- calls `_s().router.graduate(tokenAddress, ltFromPair)` which moves the curve's real raised LT out of the `Pair` into `Bonding`,
- computes and caches `tokensForLP` / `ltFromPair` in `pendingGraduation`, and
- sets `info.lifecycle = Lifecycle.Graduating` [1](#0-0) [2](#0-1) 

None of this is reversible: once committed, the only forward path is `finalizeGraduation`, which requires `info.lifecycle == Lifecycle.Graduating` and reads the *frozen* `pendingGraduation` values: [3](#0-2) 

`finalizeGraduation` calls `_ensureUniswapV2Pair` (which is a no-op if a pair already exists — anyone can pre-create it) and then `_seedUniswapV2Direct`, which explicitly documents a "Regime 3" hostile mint pre-seed defense: it rebalances via a direct `pair.swap` and deposits the balanced remainder via the router's `addLiquidity`, falling back to `_seedDirectMint` when the rebalance swap is skipped (dust quote rounds to zero, or the swap budget is zero): [4](#0-3) 

The rebalance path is capped defensively at 99% of the *swap-side* budget precisely so the deposit leg always has non-zero amounts on both sides — but this only protects the swap-and-deposit branch, not the `_seedDirectMint` fallback used when the swap is skipped against a *non-empty* pool: [5](#0-4) 

`_seedDirectMint` unconditionally transfers the fixed `(tokensForLP, ltFromPair)` amounts to the pair and calls `pair.mint(lpLock)`. Uniswap-V2-style `mint()` computes `liquidity = min(amount0 * totalSupply / reserve0, amount1 * totalSupply / reserve1)` whenever `totalSupply != 0` (i.e. the pool is *not* pristine) and reverts with `INSUFFICIENT_LIQUIDITY_MINTED` if that evaluates to `0`. Because `tokensForLP`/`ltFromPair` are pinned at phase-1's curve-close values and the attacker's pre-seeded reserves are entirely attacker-controlled and can be made arbitrarily large relative to `tokensForLP`/`ltFromPair`, the attacker can force `amount0 * totalSupply / reserve0` (or the other side) to round to `0`, causing `pair.mint()` — and therefore `finalizeGraduation` — to revert every time it is retried, since none of the inputs (pool reserves, `pendingGraduation`) can change afterward. Separately, `LPLock.recordLock` itself hard-reverts on `amount == 0` (`ZeroAmount`), so even a path that returns `liquidity == 0` without reverting inside the pair bricks the call at the very next line: [6](#0-5) 

This is the same defect class as the CVE: state is committed ("allocated") in one step — the LT drain, the token burns, and the `Lifecycle.Graduating` flag — without a corresponding cleanup/rollback if the dependent later step (`finalizeGraduation`'s LP seed + `recordLock`) permanently fails. The kernel bug forgot to clear `async_data`/the flag on the error path, leaving stale state; `Bonding` has no error path at all for a phase-2 failure — the drained LT and burned/reserved tokens are simply orphaned with the token forever stuck in `Lifecycle.Graduating` (no `buy`, `sell`, or `triggerGraduation` is possible in that state).

### Impact Explanation
All curve-raised LT (moved out of the `Pair` in phase 1 via `Router.graduate`) and the up-to-`LP_RESERVE` (250M) tokens reserved for the LP become permanently unrecoverable — no owner or user function can move them out of `Bonding` or restore the token to a tradeable state. This is a permanent freezing of trader/creator funds triggered by an unprivileged pre-seed of the HyperSwap pair, satisfying the "permanent freezing of trader, creator or LP funds" impact bar.

### Likelihood Explanation
The precondition — permissionlessly creating/seeding the HyperSwap V2 `TOKEN/LT` pair ahead of `finalizeGraduation` — is explicitly named as an in-scope, unprivileged action, and the contract's own extensive natspec acknowledges this exact "hostile mint pre-seed" threat model, showing the attack surface is real and anticipated; the specific gap is that the mitigations (99% swap-budget cap, `min=1` router deposit) only cover the swap+router-deposit branch and not the `_seedDirectMint` fallback executed against a non-empty, attacker-controlled pool.

### Recommendation
- In `_seedUniswapV2Direct`/`_seedRebalancing`, never route to `_seedDirectMint` when `IUniswapV2Pair(pair).totalSupply() != 0` (i.e., only use the "raw transfer + mint" pattern on a genuinely empty/dust pool as originally intended for Regime 1); for Regime 3 always go through the router's balanced `addLiquidity`, and if that would still yield ≤0 liquidity, escrow the funds for owner-assisted recovery instead of leaving them wedged behind a hard revert.
- Add an explicit recovery/rescue path for a token stuck in `Lifecycle.Graduating` (e.g., an owner-gated function that can re-attempt seeding with corrected parameters, or sweep the pending LT/tokens to a recovery address) so a deterministic revert in `finalizeGraduation` cannot permanently strand funds.
- Consider capping how adversarial a pre-existing pool's reserves can be relative to `tokensForLP`/`ltFromPair` before allowing the direct-mint fallback, or requiring `_ensureUniswapV2Pair`/`finalizeGraduation` to detect and reject (with a retryable, non-terminal error) a poisoned pool rather than silently falling through to an unconditional mint.

### Proof of Concept
1. Attacker (or anyone) calls `IUniswapV2Factory.createPair(token, lt)` before the target token's `canGraduate` trips, or immediately after `TokenGraduating` fires and before a keeper calls `finalizeGraduation`.
2. Attacker self-funds and calls `pair.mint(attacker)` with a reserve ratio and absolute size engineered so that, given the known/frozen `pendingGraduation.tokensForLP` and `pendingGraduation.ltFromPair` (both public via `Bonding.pendingGraduation(token)`), the rebalance swap in `_seedRebalancing` is skipped (e.g., by making one side's inventory the "protected" LT of a concurrent graduation, or by sizing the pre-seed so `_noFeeSwapInput`/`getAmountOut` round to zero) and the eventual `_seedDirectMint` call computes `min(amount0*totalSupply/reserve0, amount1*totalSupply/reserve1) == 0`.
3. Any caller invokes `Bonding.finalizeGraduation(token)`; `pair.mint(lpLock)` reverts with `INSUFFICIENT_LIQUIDITY_MINTED` (or `LPLock.recordLock` reverts with `ZeroAmount` if `liquidity` comes back as `0` without a pair-level revert).
4. Because pool reserves and `pendingGraduation` are unchanged by the failed call, every subsequent retry of `finalizeGraduation` reverts identically. The token is permanently stuck in `Lifecycle.Graduating`; the LT already moved into `Bonding` via `Router.graduate` in phase 1, and the tokens reserved for the LP, are irrecoverable.

### Citations

**File:** packages/contracts/src/Bonding.sol (L938-953)
```text
    function _enterGraduating(
        address tokenAddress
    ) internal {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        info.lifecycle = Lifecycle.Graduating;

        (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) =
            _prepareGraduationLiquidity(tokenAddress);

        $.pendingGraduation[tokenAddress] = PendingGraduation({
            tokensForLP: tokensForLP, ltFromPair: ltFromPair, lpBurned: lpBurned, unsoldBurned: unsoldBurned
        });

        emit TokenGraduating(tokenAddress, tokensForLP, ltFromPair, lpBurned, unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1000-1034)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();

        address lt = info.ltAddress;
        PendingGraduation memory p = $.pendingGraduation[tokenAddress];

        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;

        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
    }
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

**File:** packages/contracts/src/Bonding.sol (L1279-1354)
```text
    function _seedRebalancing(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));

        // Below the band on BOTH sides, overpower the pre-seed with a direct
        // mint at the cached ratio: the rebalance swap is too coarse to reach
        // the ratio against such small reserves, and the pre-existing LP's
        // claim on the deposit stays bounded by `DIRECT_MINT_PRESEED_BPS`. A
        // side that is large relative to its LP target still takes the
        // rebalance path so it isn't donated under the empty-mint `min()`.
        if (
            reserveToken * BPS_DENOM <= tokensForLP * DIRECT_MINT_PRESEED_BPS
                && reserveLT * BPS_DENOM <= ltFromPair * DIRECT_MINT_PRESEED_BPS
        ) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Budget reads `balanceOf(this)` rather than `tokensForLP` /
        // `ltFromPair` so any skim donation contributes to the rebalance
        // and not only to `_routerDepositAndDispose`'s deposit.
        // Direction: pool TOKEN-rich vs target ⇒ swap LT in (TOKEN out).
        // Pool LT-rich ⇒ swap TOKEN in (LT out). Bounded by uint112 reserves
        // and curve-close-shape targets, both products fit in uint256.
        // When `_pairRebalance` returns false the seed is too small for any
        // swap to move the ratio (its fee-charging quote rounds to zero), so
        // the reserves are negligible against this graduation's inventory:
        // overpower them with a direct mint at the cached ratio rather than
        // letting the router deposit at the attacker's ratio. A swap that
        // does fire leaves the pool ≈ at target for the router deposit.
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
        // else: pool already at curve-close ratio (rare — e.g. attacker
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
    }
```

**File:** packages/contracts/src/LPLock.sol (L70-85)
```text
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
