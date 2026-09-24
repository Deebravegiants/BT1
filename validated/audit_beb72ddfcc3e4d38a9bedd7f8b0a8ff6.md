### Title
Hostile-pre-seed mitigation is incompletely applied — `_seedRebalancing`'s dust fallback calls `_seedDirectMint` against a non-empty pool, reintroducing the LP-capture/wrong-price mint the defense exists to prevent - (`packages/contracts/src/Bonding.sol`)

### Summary
`_seedUniswapV2Direct` builds a whole rebalance-then-router-deposit mechanism specifically to stop an attacker who front-runs graduation by pre-creating the HyperSwap pair, seeding it with a hostile (TOKEN, LT) ratio, and calling `pair.mint(attacker)` before `finalizeGraduation` runs. [1](#0-0)  That mechanism, however, has two escape hatches that route back into `_seedDirectMint` — a raw `pair.mint(lpLock)` call — while `totalSupply() != 0`, i.e. while the attacker's hostile LP already exists. This reintroduces exactly the "wrong opening price" and "LP capture" harms the surrounding natspec describes as solved.

### Finding Description
`_seedUniswapV2Direct` only dispatches to `_seedRebalancing` when `IUniswapV2Pair(pair).totalSupply() != 0` — i.e. the attacker has already minted LP against a pre-seed. [2](#0-1) 

Inside `_seedRebalancing`, there are two paths that fall back to `_seedDirectMint` instead of the rebalance-then-router-deposit path:

1. When both reserve sides are below `DIRECT_MINT_PRESEED_BPS` of the target ratio, the code intentionally calls `_seedDirectMint` directly: [3](#0-2) 

2. When `_pairRebalance` returns `false` (the fee-charging swap quote rounds to zero), the code again falls back to `_seedDirectMint`: [4](#0-3) 

`_seedDirectMint` itself is documented as safe only for the empty-pool case — it transfers the *entire* cached `(tokensForLP, ltFromPair)` to the pair and calls `mint()`: [5](#0-4) 

But by construction of `_seedUniswapV2Direct`'s dispatch, every call into `_seedRebalancing` — and therefore every fallback call to `_seedDirectMint` from within it — happens when `totalSupply() > 0`. Calling V2's `mint()` against non-zero reserves and non-zero supply re-triggers the exact `min(amount0·S/r0, amount1·S/r1)` formula the whole hostile-pre-seed defense exists to defuse (documented explicitly in the natspec's regime-3 description): [6](#0-5) 

The comment on the fallback even acknowledges the donation is not eliminated, only "bounded": [7](#0-6) 

However, the bound (`DIRECT_MINT_PRESEED_BPS`) constrains the attacker's own pre-seed *size relative to the protocol's cached deposit*, not the absolute value donated. Since `tokensForLP`/`ltFromPair` (the protocol's deposit) scale with the graduation's actual raised size — up to `LP_RESERVE` (250M tokens) worth of value — an attacker can choose a cheap pre-seed ratio/size that satisfies "below-band on both sides" (or drives `_pairRebalance`'s no-fee-input calc to zero) while still collecting a share of V2's `min()` donation computed against the protocol's much larger deposit. This is precisely the "incomplete fix" pattern in the referenced external report: a mitigation exists and is documented as closing the class of bug, but a specific code path (the fallback branch) was not brought under the same protection and silently reintroduces the original vulnerability.

### Impact Explanation
A successful hostile pre-seed sized to hit either fallback branch lets the attacker's pre-existing LP position capture a pro-rata donation from the protocol's graduation deposit (tokens/LT that belong to the launched token's community and curve depositors), and opens the graduated pool at a ratio skewed away from the curve-close price — the same two harms ("wrong opening price," "LP capture") the codebase's own natspec identifies as the specific damage this subsystem prevents. [8](#0-7)  Because `LPLock` has no withdraw path, the mis-seeded reserves are also frozen once locked, compounding the damage. [9](#0-8) 

### Likelihood Explanation
`finalizeGraduation` is explicitly permissionless and callable by any address between phase 1 and phase 2, and pre-creating/pre-seeding the HyperSwap pair before graduation is a standard, unprivileged front-run available to any address, both of which are named as in-scope reachable paths. [10](#0-9)  An attacker fully controls the pre-seed ratio and size, so deliberately targeting the `DIRECT_MINT_PRESEED_BPS` band (or the `_pairRebalance`-returns-false dust case) is a matter of picking the right small numbers rather than needing any privileged access or race condition beyond the front-run window the codebase itself already documents as the standard threat.

### Recommendation
Route both fallback branches inside `_seedRebalancing` through a mint-avoiding deposit path (e.g. reuse `_routerDepositAndDispose`'s quote-based `addLiquidity`, sized to the available balances) rather than calling `pair.mint()` directly whenever `totalSupply() != 0`. If `_seedDirectMint` must remain shared code, gate its raw-`mint()` call on `totalSupply() == 0` and give the non-empty-pool fallbacks their own logic that never re-triggers V2's `min()` donation formula. At minimum, tighten `DIRECT_MINT_PRESEED_BPS` and audit `_pairRebalance`'s zero-return conditions against realistic graduation deposit sizes to bound the donation to genuinely negligible absolute value, and restore/replace the removed `test/HostilePreSeed.t.sol` coverage for both fallback branches specifically.

### Proof of Concept
1. Attacker front-runs a token nearing graduation: calls `factory.createPair(token, lt)`, then transfers a small `TOKEN`/`LT` pair sized so that both `reserveToken * BPS_DENOM <= tokensForLP * DIRECT_MINT_PRESEED_BPS` and `reserveLT * BPS_DENOM <= ltFromPair * DIRECT_MINT_PRESEED_BPS` will hold once `_enterGraduating` caches `tokensForLP`/`ltFromPair` for that token (attacker can estimate these from the curve's current reserves, which are public), then calls `pair.mint(attacker)` to become the pool's sole LP holder at a hostile ratio.
2. The threshold-crossing buy fires `_enterGraduating`, caching `pendingGraduation[token]`. [11](#0-10) 
3. Anyone (attacker or keeper) calls `finalizeGraduation(token)`. Because `totalSupply() != 0`, dispatch goes to `_seedRebalancing`, which detects both sides below `DIRECT_MINT_PRESEED_BPS` and calls `_seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair)` directly against the non-empty pool. [3](#0-2) 
4. `pair.mint(lpLock)` computes `liquidity = min(amount0·totalSupply/reserve0, amount1·totalSupply/reserve1)` against the attacker's existing tiny reserves and supply, donating the "excess" side's value pro-rata to existing LP holders — 100% the attacker — while opening the pool at `(reserve+deposit)` ratio rather than the cached curve-close ratio.
5. The attacker's LP position (held outside `LPLock`, since it was minted to `attacker`, not `lpLock`, in step 1) now embeds value donated from the protocol's `tokensForLP`/`ltFromPair` deposit, extractable via `removeLiquidity` on the HyperSwap pair — concrete theft of trader/creator funds meant to seed the graduated LP.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1023)
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

**File:** packages/contracts/src/Bonding.sol (L1132-1176)
```text
    /// @dev LP-seeding into the HyperSwap pair, hardened against hostile
    ///      pre-seeds. Three regimes:
    ///
    ///        1. **No LP minted yet — `totalSupply == 0` (~99% of
    ///           graduations).** A pristine empty pair, or a dust pre-seed
    ///           (`transfer(pair, dust) + sync()` leaves `reserves > 0` but
    ///           `totalSupply == 0`). Direct mint at exactly
    ///           `(tokensForLP, ltFromPair)` — V2's first-liquidity branch
    ///           makes those amounts the sole price input, so the pool opens
    ///           at the curve-close ratio and any dust becomes reserves with
    ///           no LP claim.
    ///        2. **Pure-donation pre-seed.** Attacker `transfer`'d to the
    ///           pair without `mint` (balance > 0, reserves == 0).
    ///           `pair.skim(address(this))` pulls the donation into
    ///           `Bonding`; path then collapses to (1). Donated TOKEN is
    ///           burned alongside the empty-pair mint; donated LT is
    ///           handled by `finalizeGraduation`'s post-bookend
    ///           `_sweepLTToOwner` (which uses `protectedLT` snapshotted
    ///           BEFORE skim, so the donation is correctly classified as
    ///           rebalance residue rather than concurrent-graduation
    ///           escrow). NEVER routed to `LPLock` — `LPLock` has no
    ///           rescue path in v1, so anything that lands there is
    ///           permanently stuck.
    ///        3. **Mint pre-seed.** Attacker called `pair.mint` against a
    ///           self-funded seed, baking a hostile (TOKEN, LT) ratio into
    ///           the pool. Without intervention `pair.mint(lpLock)`'s
    ///           `min(amount0·S/r0, amount1·S/r1)` formula would (a) open
    ///           the LP off curve-close-price and (b) donate the larger arm
    ///           to the attacker's pre-existing LP. We rebalance via a
    ///           direct `pair.swap` toward the curve-close ratio, then
    ///           deposit the remaining inventory via the router's
    ///           `quote()`-based `addLiquidity` — which only pulls the
    ///           optimal amounts at the post-swap ratio, so neither side
    ///           becomes a `min()` donation. Off-ratio TOKEN remainder is
    ///           burned; off-ratio LT remainder is auto-swept to the owner
    ///           by `finalizeGraduation`'s post-bookend (see its natspec).
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

**File:** packages/contracts/src/Bonding.sol (L1217-1234)
```text
        // Regime 1 — no LP minted yet (`totalSupply == 0`): a pristine empty
        // pair, or a dust pre-seed from `transfer(pair, dust) + sync()` that
        // leaves reserves non-zero while supply is still zero. Keying on
        // supply rather than reserves routes the dust shape here instead of
        // the rebalance path: with zero supply V2 mints from our amounts
        // alone, so the pool opens at the cached ratio and any dust becomes
        // reserves with no LP claim.
        if (IUniswapV2Pair(pair).totalSupply() == 0) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Regime 3 — mint pre-seed: rebalance, then deposit balanced subset.
        // `lpLock_` re-read from storage inside `_routerDepositAndDispose`.
        // Reserves and token-ordering re-read inside `_seedRebalancing` to
        // keep this function's stack pressure under solc's 16-slot ceiling
        // without `viaIR`.
        return _seedRebalancing(tokenAddress, lt, pair, tokensForLP, ltFromPair, protectedLT);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1236-1259)
```text
    /// @dev Transfer the full `(tokensForLP, ltFromPair)` to the pair and
    ///      `mint` the LP to `LPLock`, opening at the exact cached
    ///      curve-close ratio. Used by the empty-pair regime and as the
    ///      dust-pre-seed fallback in `_seedRebalancing` — against dust
    ///      reserves the V2 `min()` formula's donation to any pre-existing
    ///      LP is negligible (see `_seedUniswapV2Direct` natspec). Any TOKEN
    ///      remainder (a skimmed pure-donation pre-seed) is burned; the LT
    ///      remainder is left for `finalizeGraduation`'s `_sweepLTToOwner`
    ///      post-bookend.
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

**File:** packages/contracts/src/Bonding.sol (L1291-1302)
```text
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
```

**File:** packages/contracts/src/Bonding.sol (L1316-1332)
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
```

**File:** packages/contracts/src/LPLock.sol (L9-15)
```text
/// @notice Locks LP tokens from graduated tokens. No withdraw in v1.
/// @dev UUPS-upgradeable to support v2 `migrateLT` functionality.
///      Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
```
