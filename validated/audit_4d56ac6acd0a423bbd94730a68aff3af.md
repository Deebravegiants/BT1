### Title
Rounding to zero in `tokensForLP` computation can permanently brick `finalizeGraduation`, stranding raised LT and the token forever in `Lifecycle.Graduating` - ([File: packages/contracts/src/Bonding.sol])

### Summary
The original report's bug class is: an entity (a validator) can be written into persistent state without being checked for validity, the checking code then errors out, but the invalid entity is never removed — leaving the store permanently corrupted. `Bonding.sol` has a structurally analogous defect in its two-phase graduation flow: phase 1 (`_enterGraduating`) commits an irreversible lifecycle transition and caches unvalidated LP-seeding amounts in `pendingGraduation` before phase 2 ever runs; phase 2 (`finalizeGraduation`) can revert permanently on those cached values, and there is no code path to remove/repair the bad `pendingGraduation` entry or revert the lifecycle back to `Curve`.

### Finding Description
`_enterGraduating` is called permissionlessly (via `triggerGraduation`) or inline from a threshold-crossing `buy()`, and it unconditionally commits state that can never be undone: [1](#0-0) 

The cached amounts come from `_prepareGraduationLiquidity`, in particular: [2](#0-1) 

`tokensForLP = (ltFromPair * tokenReserve) / assetReserve` truncates to `0` in integer division whenever `tokenReserve * ltFromPair < assetReserve`. This is reachable in ordinary trading: as the curve sells down toward depletion, `tokenReserve` (remaining unsold curve tokens) shrinks toward zero while `assetReserve` (accumulated LT, including the large virtual seed) stays large. A buy that crosses the USD graduation threshold (or, in the extreme, the supply trigger via `IPair(pair).tokenBalance() == 0`) while `tokenReserve` is small relative to `assetReserve` produces `tokensForLP == 0` while `ltFromPair > 0`. `_prepareGraduationLiquidity` has no check to reject or clamp this degenerate value — it is written straight into `PendingGraduation` and the lifecycle is flipped to `Graduating`, exactly like `insertValidatorSet` writing an unvalidated entry before any error is raised.

Phase 2, `finalizeGraduation`, then reads this cached, unvalidated `PendingGraduation` and drives LP seeding through `_seedUniswapV2Direct` → `_seedDirectMint` on the empty-pair path (the common case for a normal graduation): [3](#0-2) 

With `tokensForLP == 0` and `ltFromPair > 0`, `IUniswapV2Pair(pair).mint(...)` computes `liquidity = sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY = sqrt(0) - 1000`, which underflows and reverts (`INSUFFICIENT_LIQUIDITY_MINTED` in standard V2 pair code). Every retry of `finalizeGraduation` re-reads the same frozen `PendingGraduation` values (they are only mutated by `_enterGraduating`, which cannot run again because `info.lifecycle == Lifecycle.Graduating` is checked and rejected everywhere: `buy`, `sell`, and `triggerGraduation` all revert with `TokenIsGraduating`/`NotGraduatable` once lifecycle has left `Curve`): [4](#0-3) [5](#0-4) 

There is no owner or permissionless function anywhere in `Bonding.sol` that can reset `pendingGraduation[tokenAddress]`, revert `Lifecycle` back to `Curve`, or otherwise repair the stuck entry — the exact "insert an invalid entity, then the validating step errors, but nothing removes it" pattern from the source report, just expressed across two phases of an irreversible on-chain state machine instead of a single Cosmos SDK keeper call.

### Impact Explanation
Once this triggers, the token is permanently stuck in `Lifecycle.Graduating`:
- Trading is frozen forever (`buy`/`sell` both reject `Lifecycle.Graduating`).
- All curve-raised LT that was moved out of the `Pair` via `_s().router.graduate(tokenAddress, ltFromPair)` in `_prepareGraduationLiquidity` (line 1086) is parked inside `Bonding` with no recall path — this is real value contributed by every buyer on the curve.
- The 250M (`LP_RESERVE`)-scoped token allocation intended for the LP is likewise stranded/unusable.
- No admin or permissionless recovery function exists to un-stick the token.

This is a permanent freeze of trader- and creator-contributed funds (the LT raised by the curve), satisfying the "permanent freezing of trader, creator or LP funds" acceptance bar.

### Likelihood Explanation
No privileged action or attacker capital is required. Any unprivileged trader whose ordinary `Zap.buy` pushes the curve's `tokenReserve` low enough relative to `assetReserve` at the moment the USD or supply trigger fires can cause `tokensForLP` to floor to `0` in `_prepareGraduationLiquidity`'s integer division. Because `LP_RESERVE` is a small, fixed fraction of `tokenReserve`'s dynamic range and the division has no minimum-output guard, this is a plain rounding edge case in normal curve depletion near full sellout, not a contrived adversarial construction — it can also be intentionally triggered by a trader executing a buy sized to land the curve exactly at that ratio.

### Recommendation
In `_prepareGraduationLiquidity`, validate the computed LP-seeding amounts before committing them to `pendingGraduation`/flipping the lifecycle — e.g., require `tokensForLP > 0` (and `ltFromPair > 0`) or apply a floor/round-up instead of round-down so the LP-seed amounts can never degenerate to a value that makes `IUniswapV2Pair.mint` revert. Additionally, add a permissionless or owner-gated recovery path that can retry/repair a `Lifecycle.Graduating` token whose cached `PendingGraduation` values are unseedable, so a single bad rounding outcome cannot permanently brick the token, mirroring the recommended fix in the source report (validate before insert, and provide a way to remove/repair invalid entries).

### Proof of Concept
1. Launch a token via `Zap.createToken`/`Bonding.launch` normally.
2. Have an unprivileged trader (or a sequence of buys) drive the curve via `Zap.buy` → `Bonding.buy` → `Router.buy` such that, at the exact buy that satisfies `canGraduate` (USD threshold crossed, or `IPair.tokenBalance() == 0`), the pair's `tokenReserve` is small enough that `(ltFromPair * tokenReserve) / assetReserve` truncates to `0` in `Bonding._prepareGraduationLiquidity` (Bonding.sol:1089).
3. `_executeBuy` observes `canGraduate == true` and calls `_enterGraduating`, which stores `PendingGraduation{tokensForLP: 0, ltFromPair: X>0, ...}` and sets `info.lifecycle = Lifecycle.Graduating` (Bonding.sol:938-953) — this state is now committed on-chain.
4. Anyone calls `finalizeGraduation(tokenAddress)`. It reaches the empty-pair branch and calls `_seedDirectMint` with `tokensForLP = 0`, `ltFromPair = X` (Bonding.sol:1245-1259), which calls `IUniswapV2Pair(pair).mint(lpLock)`; standard Uniswap V2 `mint` reverts with `INSUFFICIENT_LIQUIDITY_MINTED` because `sqrt(0 * X) < MINIMUM_LIQUIDITY`.
5. Every subsequent call to `finalizeGraduation` re-derives the identical `tokensForLP = 0` from the frozen `pendingGraduation[tokenAddress]` and reverts identically. `triggerGraduation`, `buy`, and `sell` all reject because `info.lifecycle != Lifecycle.Curve`. The token, and the LT it raised (already moved into `Bonding` via `router.graduate`), are permanently stuck with no recovery function in the contract.

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

**File:** packages/contracts/src/Bonding.sol (L973-979)
```text
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
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

**File:** packages/contracts/src/Bonding.sol (L1084-1096)
```text
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
