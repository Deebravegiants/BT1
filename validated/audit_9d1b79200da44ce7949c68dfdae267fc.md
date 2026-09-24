### Title
Direct LT donations to the curve `Pair` become permanently locked once graduation's fixed accounting drains and finalizes the curve - ([File: packages/contracts/src/Bonding.sol], [File: packages/contracts/src/Pair.sol])

### Summary
`Bonding._prepareGraduationLiquidity` fixes `ltFromPair` as `assetReserve - virtualLtReserve` (derived from the pair's *stored* reserves) at the moment graduation phase 1 fires, and drains exactly that amount via `Router.graduate` → `Pair.transferAsset`. Any LT sent to the pair via a direct ERC20 transfer (a donation) is excluded from this accounting because it inflates only the pair's live `balanceOf`, not `_pool.assetReserve`. `Pair.transferAsset` can only be called by `Router`, gated to callers holding `BONDING_ROLE`, and the only caller in the whole system that ever invokes `Router.graduate` for a given token is `Bonding._prepareGraduationLiquidity`, which runs exactly once per token during phase 1 of graduation (`Lifecycle.Curve → Graduating`). Once that one-shot call has fired, `Bonding` never calls `Router.graduate` for that token again, and after `finalizeGraduation` the token is `Lifecycle.Graduated` with trading permanently moved to the HyperSwap pool. Any LT sitting in the (now dead) curve `Pair` — whether donated before or after phase 1 — has no code path left that can ever move it out of the pair. This directly mirrors the analog bug class: value added to a pool ("funding") whose distribution/accounting logic was already fixed at a point in time becomes permanently unrecoverable.

### Finding Description
- `Bonding.canGraduate` / `_prepareGraduationLiquidity` compute `ltFromPair = assetReserve - virtualLtReserve` using the pair's **stored** reserves (`IPair.getReserves()`), not the live token balance: [1](#0-0) 
- The docs explicitly confirm this design: donated LT "remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`" under "the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation": [2](#0-1) 
- `Pair.transferAsset` is the only function that can ever move the LT balance out of the pair, and it's restricted to `onlyRouter`: [3](#0-2) 
- `finalizeGraduation` flips lifecycle to `Graduated` and deletes `pendingGraduation`; there is no subsequent code path in `Bonding` that revisits the drained curve `Pair` for that token to sweep any residual LT balance: [4](#0-3) 

Because `assetReserve` (the accounting figure used for `ltFromPair`) is frozen at whatever the curve's swap-tracked reserve was at the moment phase 1 fires, any LT balance in the pair beyond that figure — whether it arrived via an ordinary `IERC20.transfer` donation before phase 1, or is transferred into the pair *after* phase 1 (since nothing prevents a plain ERC20 transfer targeting the pair address at any time, even after `Lifecycle.Graduating`/`Graduated`) — is excluded from `Router.graduate`'s drain and from any future draining, because that call only ever fires once per token.

### Impact Explanation
Any LT tokens transferred directly to a curve `Pair` contract address that are not captured by the stored-reserve-based `ltFromPair` calculation are permanently and irrecoverably locked — there is no owner/admin/permissionless rescue function targeting the curve `Pair`'s asset balance once the pair's one graduation event has consumed and moved past `Lifecycle.Graduating`. This is unbacked, permanently frozen value belonging to whoever sent it (an unrelated wallet, or even the pool itself accumulating dust/rounding residue over many buys/sells). This satisfies the "permanent freezing of trader/creator/LP funds" bar in the validation criteria.

### Likelihood Explanation
Reaching this requires only a plain, permissionless ERC20 `transfer` of the LT token to the `Pair` address — explicitly listed as an in-scope reachable action ("direct ERC20 transfers of ... an LT into Pair"). No privileged role, no upgrade, and no unusual sequencing is needed: any wallet holding LT can send it to a known `Pair` address at any time (before phase 1 fires, during the `Graduating` window, or even after `Graduated`), and the funds are stuck as soon as the one-shot `Router.graduate` call has already executed (or will only ever execute once for that reserve snapshot). The protocol's own documentation acknowledges this exact accounting boundary and explicitly relies on it never being revisited, confirming the root cause and that it is an accepted (but real) permanent-loss condition rather than a hypothetical.

### Recommendation
Add a permissionless (or owner-gated) sweep function reachable only after `Lifecycle.Graduated` that transfers any residual LT balance in the curve `Pair` (`assetBalance() - 0`, since `ltFromPair` was already drained to exactly the accounted amount) to a designated recipient (e.g., `FeeVault` or the token's creator/protocol owner), analogous to `Bonding._sweepLTToOwner` already used for the HyperSwap-side residue. This closes the gap where donation dust or late transfers into a fully drained, permanently-`Graduated` pair can never be retrieved by anyone.

### Proof of Concept
1. Creator launches a token via `Zap.createToken`, curve trades normally.
2. At any point — before or after the curve crosses the graduation threshold — an unrelated wallet calls `LT.transfer(pairAddress, donationAmount)` directly (no interaction with `Bonding`/`Router` needed).
3. A subsequent buy (or a permissionless `Bonding.triggerGraduation` call) fires phase 1: `_prepareGraduationLiquidity` computes `ltFromPair = assetReserve - virtualLtReserve` from the pair's *stored* reserves — this excludes `donationAmount`, which only affected the pair's live `balanceOf`, not `_pool.assetReserve` [5](#0-4) .
4. `Router.graduate` drains exactly `ltFromPair` via `Pair.transferAsset`, leaving `donationAmount` behind in the pair [3](#0-2) .
5. Anyone calls `finalizeGraduation`, flipping the token to `Lifecycle.Graduated` and deleting `pendingGraduation` [6](#0-5) .
6. `donationAmount` now sits in the `Pair` contract forever: `Pair.transferAsset` is `onlyRouter`, and no code in `Bonding`/`Router` will ever call `Router.graduate` for this token again — the LT is permanently unrecoverable by any party.

### Citations

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

**File:** docs/contracts-scope.md (L89-89)
```markdown
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
```

**File:** packages/contracts/src/Pair.sol (L81-86)
```text
    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }
```
