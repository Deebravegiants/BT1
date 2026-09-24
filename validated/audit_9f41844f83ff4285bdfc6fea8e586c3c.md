## Title
Concurrent-graduation LT escrow can be consumed by another token's hostile-preseed rebalance swap in `Bonding._seedRebalancing` / `_pairRebalance` - (File: packages/contracts/src/Bonding.sol)

### Summary
`finalizeGraduation` explicitly protects a concurrent graduation's escrowed LT via the `protectedLT` snapshot before doing any deposit, but the swap-budget calculation in the hostile-pre-seed rebalance path (`_seedRebalancing` → `_pairRebalance`) is documented to read the raw `balanceOf(this)` instead of netting out `protectedLT`. This is the same root-cause class as the C4 finding: a fee/payment for one operation is drawn against the *shared* contract balance rather than the funds actually earmarked for that operation, so a second, unrelated operation's escrowed funds get consumed/misallocated.

### Finding Description
`Bonding.finalizeGraduation` computes `protectedLT` as "any LT balance beyond this graduation's `ltFromPair`", explicitly to isolate a concurrent graduation's escrow on a shared LT: [1](#0-0) 

The natspec in `packages/contracts/AGENTS.md` spells out exactly this scenario — "Two tokens A and B share an LT and both reach `Lifecycle.Graduating` before either finalizes... Without `protectedLT`, A's finalize would treat the full balance as its own": [2](#0-1) 

The router-deposit leg of the seeding correctly nets out `protectedLT` from the balance it's allowed to spend (`_routerDepositAndDispose`'s deposit allowance is "capped at `balanceOf(this) - protectedLT`"), per the same AGENTS.md section. However, the earlier hostile-mint-preseed rebalance leg — `_seedRebalancing`, which fires before `_routerDepositAndDispose` when `pair.totalSupply() != 0` — is documented to size its swap input off the raw contract balance, not the graduation-scoped earmark: [3](#0-2) 

The comment at lines 1304-1306 states: "Budget reads `balanceOf(this)` rather than `tokensForLP` / `ltFromPair` so any skim donation contributes to the rebalance and not only to `_routerDepositAndDispose`'s deposit." This is a self-admitted asymmetry: `protectedLT` is threaded through as a parameter to `_seedRebalancing` (and further to `_seedUniswapV2Direct`), but per this comment it is used only to gate the direct-mint fallback decision, not to cap the swap-input budget that ultimately feeds `_pairRebalance`'s `pair.swap` call. If token A's finalize hits the rebalance branch while token B (sharing the same LT) is sitting in `Lifecycle.Graduating` with its `ltFromPair_B` already escrowed in `Bonding` via `Router.graduate` (called from `_enterGraduating`/`_prepareGraduationLiquidity`), A's rebalance swap can consume LT that is actually B's escrow, since the budget is computed from the undifferentiated `balanceOf(this)`.

### Impact Explanation
If the swap budget in the rebalance leg is not netted against `protectedLT`, token A's hostile-preseed rebalance swap can spend LT that belongs to token B's pending graduation. Two concrete harms follow: (1) B's later `finalizeGraduation` reads `ltBalance = IERC20(lt).balanceOf(address(this))` and computes `protectedLT`/deposit off a balance now short by whatever A's rebalance consumed, so B's LP seeds with less LT than the cached `ltFromPair_B`, breaking the zero-price-gap invariant and potentially reverting/bricking B's deposit if the shortfall is large; or (2) B's rightful LT is effectively swapped into A's pool inventory/rebalance, i.e., value transferred from B's raised curve reserve into A's LP, a direct loss of funds for token B's creator/holders. This is the same shape as the C4 High: a payment (here, the rebalance swap input) is funded from the shared pool instead of the caller/operation's own earmarked funds, at the expense of a concurrent unrelated operation.

### Likelihood Explanation
Reaching the vulnerable state only requires ordinary, permissionless actions: (a) launch two tokens against the same BounceTech LT via `Zap.createToken`/`Bonding.launch`, (b) buy on both curves until both graduate phase 1 (`triggerGraduation` or the inline threshold-crossing buy) so both sit in `Lifecycle.Graduating` with LT escrowed in `Bonding` at the same time — explicitly called out as a realistic occurrence in the project's own docs ("popular LTs see overlap" during the ~60s keeper window), and (c) ensure one of the two pairs has a non-empty V2 pool (e.g., attacker- or third-party-seeded, or simply already graduated once with residual dust reserves) so `finalizeGraduation` on that token takes the `_seedRebalancing` hostile-preseed branch instead of the empty-pair direct-mint path. All of these are permissionless, unprivileged actions (`Zap.createToken`, `Bonding.buy`, `Bonding.triggerGraduation`, `Bonding.finalizeGraduation`, plus pre-seeding the HyperSwap pair — all explicitly in the allowed analog surface).

### Recommendation
Cap the rebalance-swap's input budget (the `maxSwap` computed in `_seedRebalancing` and consumed by `_pairRebalance`) by `balanceOf(this) - protectedLT`, exactly as `_routerDepositAndDispose`'s deposit allowance already does, so the rebalance swap can never spend LT earmarked for a concurrent graduation on the same LT. Add a dedicated regression test (concurrent graduations on the same LT where the first one to finalize hits the hostile-preseed rebalance path) to `TwoPhaseGraduation.t.sol`/`GraduationInvariants.t.sol` asserting the second token's `ltFromPair` is fully preserved through the first token's `finalizeGraduation`.

### Proof of Concept
1. Deploy one BounceTech LT; launch token A and token B against it via `Zap.createToken` (two independent bonding curves, same reserve LT).
2. Buy on curve A until it crosses the graduation threshold; call `Bonding.triggerGraduation(A)` — phase 1 drains A's curve LT into `Bonding` via `Router.graduate`, caches `pendingGraduation[A].ltFromPair`.
3. Before calling `finalizeGraduation(A)`, buy on curve B until it also crosses the threshold; call `Bonding.triggerGraduation(B)` — phase 1 drains B's curve LT into the same `Bonding` contract, on top of A's still-un-finalized escrow. `Bonding`'s LT balance now equals `ltFromPair_A + ltFromPair_B`.
4. Ensure A's HyperSwap V2 TOKEN/LT pair already has non-zero `totalSupply` (e.g., pre-seed it with a small `pair.mint` from an unrelated wallet before phase 2, per the documented hostile-mint-preseed regime) so `finalizeGraduation(A)` takes the `_seedRebalancing` branch rather than `_seedDirectMint`.
5. Call `finalizeGraduation(A)`. Per the code comment, the rebalance swap's input budget is sized off `IERC20(lt).balanceOf(address(this))` (i.e., `ltFromPair_A + ltFromPair_B`) rather than `balanceOf(this) - protectedLT` (`ltFromPair_A` only), so the swap can consume more LT than A is entitled to, encroaching on `ltFromPair_B`.
6. Call `finalizeGraduation(B)` afterward and observe its LP is seeded with less LT than the cached `pendingGraduation[B].ltFromPair`, breaking the zero-price-gap invariant, or that B's `_routerDepositAndDispose`/`_sweepLTToOwner` accounting is now inconsistent with the pre-computed `ltFromPair_B`, demonstrating value drained from B's escrow into A's finalize. [4](#0-3)

### Citations

**File:** packages/contracts/src/Bonding.sol (L1010-1023)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1201-1234)
```text
    function _seedUniswapV2Direct(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        // Regime 2 — pull any donation pre-seed into this contract so it
        // doesn't pollute the post-swap ratio. Routed to `address(this)`
        // (NOT `lpLock`) so donated TOKEN can be burned and donated LT
        // can be swept to the owner via `_sweepLTToOwner` — `LPLock` has
        // no rescue path, so anything sent there is permanently stuck.
        // No-op on a freshly-created pair (balance == reserves == 0).
        IUniswapV2Pair(pair).skim(address(this));

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

**File:** packages/contracts/src/Bonding.sol (L1279-1316)
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
```

**File:** packages/contracts/AGENTS.md (L211-219)
```markdown

`finalizeGraduation` snapshots `protectedLT = balanceOf(this) - p.ltFromPair` at the top: any LT in `Bonding` beyond this graduation's earmark is either another concurrent graduation's escrow (Phase 1 already moved it in via `Router.graduate`) or stray dust. Both must stay out of THIS graduation's LP and post-sweep.

That snapshot is plumbed through `_seedUniswapV2Direct` → `_seedRebalancing` → `_routerDepositAndDispose`, where the deposit allowance is capped at `balanceOf(this) - protectedLT`. Then a single `_sweepLTToOwner(lt, protectedLT)` at the end of `finalizeGraduation` sends only THIS graduation's rebalance residue to the protocol owner, leaving any concurrent-graduation escrow / stray dust untouched. Honest empty-pair graduations have no residue at the post-sweep so it's a no-op there.

Two scenarios this guards against:

- **Concurrent graduations on the same LT.** Two tokens A and B share an LT and both reach `Lifecycle.Graduating` before either finalizes (the keeper takes ~60s and popular LTs see overlap). Without `protectedLT`, A's finalize would treat the full balance as its own and either sweep B's escrow to the owner (bricking B's later finalize) or — for hostile-pre-seed graduations — deposit it into A's locked LP. With it, A only ever sees `ltFromPair_A` and B is preserved.
- **Cross-token LT residue.** Old residue or a misdirected transfer sitting in `Bonding` would otherwise be visible to `_routerDepositAndDispose`'s `balanceOf(this)` read and could be silently consumed into a future graduation's locked LP. With `protectedLT`, contamination stays in `Bonding` and the deposit only sees this graduation's earmark.
```
