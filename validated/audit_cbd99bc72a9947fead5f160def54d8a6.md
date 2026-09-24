## Analysis

The Y2K report's bug class — value transferred into a contract that becomes permanently unrecoverable once the contract reaches a terminal state with no sweep path — maps directly onto alt.fun's curve `Pair` and the LT reserve asset.

### Root cause

`Pair.sol` tracks LT reserves via an internal `_pool.assetReserve` field, separate from the LT's live `balanceOf(this)`: [1](#0-0) 

The only function capable of moving the LT (`assetToken`) out of the `Pair` is `transferAsset`, gated `onlyRouter`: [2](#0-1) 

`Router.graduate` is the sole caller of `transferAsset` for the asset side, and it is itself only ever invoked from `Bonding._prepareGraduationLiquidity`: [3](#0-2) 

`_prepareGraduationLiquidity` computes the amount to drain from **stored** reserves, not the live LT balance, explicitly excluding any LT that was donated directly to the pair via `IERC20.transfer`: [4](#0-3) 

This function is reachable exactly once per token: it only runs from `_enterGraduating`, which is only reachable while `lifecycle == Lifecycle.Curve` (via `_executeBuy`'s post-buy check or the permissionless `triggerGraduation`). Once the lifecycle flips to `Graduating`/`Graduated`, `_enterGraduating`/`_prepareGraduationLiquidity`/`Router.graduate` can never run again for that token: [5](#0-4) 

The project's own docs confirm this is a deliberate but acknowledged trust-assumption, not an on-chain guarantee, and that no rescue path exists for LT stuck in the curve pair: [6](#0-5) [7](#0-6) 

`Pair.sol` has no `skim`/`sync`/admin-rescue function at all — unlike the HyperSwap-side handling in `Bonding._seedUniswapV2Direct`, which does pull donations into `Bonding` via `pair.skim`. There is no equivalent for the curve `Pair`.

### Why this is a valid analog

Any unprivileged wallet performing a plain `IERC20(lt).transfer(curvePairAddress, amount)` — one of the explicitly allowed reachable actions — permanently strands that LT the moment the token graduates (or forever, for a token that never graduates and is abandoned), with zero code path to recover it. This is the direct structural analog of the Sherlock report's `emissionsToken` remaining stuck when `NullEpoch` fires with no withdraw path: value sent into a contract, no NullEpoch-style trigger reachable to sweep it back out.

---

### Title
Leveraged Token (LT) donated directly to the curve `Pair` is permanently locked with no sweep path after graduation - (File: `packages/contracts/src/Pair.sol`, `packages/contracts/src/Bonding.sol`, `packages/contracts/src/Router.sol`)

### Summary
LT sent directly to a bonding-curve `Pair` (bypassing `Zap`/`Bonding.buy`) is excluded from the stored-reserve accounting used at graduation, and once a token's `lifecycle` leaves `Curve`, the only function capable of moving LT out of that `Pair` (`Router.graduate`, itself only callable from `Bonding._prepareGraduationLiquidity`) becomes permanently unreachable. The donated LT is frozen in the `Pair` contract forever.

### Finding Description
`Pair` stores reserves in `_pool.tokenReserve`/`_pool.assetReserve`, distinct from live ERC20 balances. `_prepareGraduationLiquidity` computes `ltFromPair = assetReserve - virtualLtReserve` from the *stored* `assetReserve`, so any LT balance in excess of that (i.e., a direct `transfer` donation) is intentionally left behind in the `Pair`. `_prepareGraduationLiquidity` is only invoked once, from `_enterGraduating`, which is only reachable while `lifecycle == Curve`. After graduation (`lifecycle == Graduated`), no code path calls `Router.graduate` (or any other `Pair.transferAsset`) for that pair again. `Pair.sol` itself exposes no `skim`, `sync`, or owner-rescue function for the asset side. Consequently, LT sent to the pair after the token has graduated, or LT donated before graduation that exceeds the amount swept at `_prepareGraduationLiquidity` time due to rounding, is permanently stranded — there is no privileged or permissionless function anywhere in scope that can move it out.

### Impact Explanation
This is a permanent freezing-of-funds bug matching the Sherlock report's class exactly: value transferred into the protocol's contracts becomes unrecoverable once the associated state machine passes a terminal transition with no corresponding sweep. Any LT (a real, valuable ERC20 reserve asset) sent to a graduated (or never-to-graduate) curve `Pair` is burned economically — dead capital with no owner-controlled or user-controlled recovery mechanism.

### Likelihood Explanation
Reachable by any unprivileged wallet via a single `IERC20(lt).transfer(pair, amount)` call — no special permissions, no attacker collusion, and no dependency on BounceTech LT or HyperSwap internals required. It can happen accidentally (a user or integrator mistakenly sending LT to the pair address instead of through `Zap`) or be triggered deliberately post-graduation, at which point the loss is deterministic and irreversible.

### Recommendation
Add a permissionless sweep function on `Pair` (or a `Bonding`-level rescue callable via `Router`, gated to only run once `lifecycle == Graduated` so it cannot interfere with the live curve's K-invariant) that transfers any LT balance in the `Pair` above the last-known/zero stored `assetReserve` to a safe recipient (e.g., `owner()` or back to the depositor via an on-chain donation-tracking mechanism), mirroring the `skim`-then-integrate pattern already used for the HyperSwap pair in `Bonding._seedUniswapV2Direct`.

### Proof of Concept
1. Launch a token via `Bonding.launch`/`Zap.createToken`, obtaining `tokenAddr` and its curve `pairAddr`.
2. Anyone (attacker, integrator error, or the LT contract itself via a rebase/airdrop) calls `IERC20(lt).transfer(pairAddr, X)` directly, bypassing `Zap`/`Bonding.buy`. `Pair._pool.assetReserve` is untouched by a raw `transfer` (only `swap`/`mint` mutate it), so `X` sits in `pairAddr`'s LT balance above the accounted reserve.
3. Drive the token to graduation (`Bonding.triggerGraduation` / threshold-crossing buy) and call `finalizeGraduation`. `_prepareGraduationLiquidity` computes `ltFromPair` from `_pool.assetReserve` only, drains exactly that via `Router.graduate`, and leaves `X` behind in `pairAddr`.
4. `lifecycle[tokenAddr]` is now `Graduated`. Confirm no remaining function in `Bonding`, `Router`, or `Pair` can call `transferAsset` on `pairAddr` again (`_enterGraduating`/`triggerGraduation` revert with `TokenNotTrading`/`TokenIsGraduating` once past `Curve`, and `Pair` exposes no `skim`/`sync`/owner rescue).
5. `X` LT remains in `pairAddr` permanently, with `IERC20(lt).balanceOf(pairAddr) > 0` and no transaction able to move it out.

### Citations

**File:** packages/contracts/src/Pair.sol (L21-27)
```text
    struct Pool {
        uint256 tokenReserve;
        uint256 assetReserve;
        uint256 k;
    }

    Pool private _pool;
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

**File:** packages/contracts/src/Router.sol (L184-202)
```text
    /// @notice Transfer exactly `amount` of LT out of the pair to the caller.
    ///         Called by `Bonding._prepareGraduationLiquidity` during graduation
    ///         with `amount = stored assetReserve - virtualLtReserve` (i.e. the
    ///         real LT raised by the curve, excluding the virtual seed).
    /// @dev    Donation-resistant: passing an explicit `amount` instead of
    ///         draining `assetBalance()` ensures any LT that was donated
    ///         directly to the pair via `IERC20.transfer` is left behind and
    ///         excluded from LP seeding.
    ///
    ///         "Locked" here is a trust-assumption claim, not an on-chain
    ///         guarantee. `Pair.transferAsset` is gated by `onlyRouter`, and
    ///         `Router` only exposes it via this function and `sell`. Both
    ///         require `BONDING_ROLE`, which only `Bonding` holds. `Bonding`
    ///         in turn only calls `graduate` from
    ///         `_prepareGraduationLiquidity` — which is unreachable once the
    ///         token's lifecycle has flipped past `Curve`. So the leftover
    ///         is unreachable as long as (a) `BONDING_ROLE` is not granted
    ///         to any other address, and (b) future `Bonding` upgrades
    ///         preserve the lifecycle gate.
```

**File:** packages/contracts/src/Router.sol (L203-211)
```text
    function graduate(
        address token,
        uint256 amount
    ) external onlyRole(BONDING_ROLE) {
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        IPair(pairAddr).transferAsset(msg.sender, amount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L970-979)
```text
    function triggerGraduation(
        address tokenAddress
    ) external nonReentrant {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1073-1090)
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
```

**File:** docs/contracts-scope.md (L88-89)
```markdown
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
```
