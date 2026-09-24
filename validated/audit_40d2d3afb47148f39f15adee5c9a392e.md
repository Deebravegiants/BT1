I found a genuine structural analog to the CVE's "shared resource between two independently-controlled domains" bug class in `Bonding.sol`'s handling of concurrent graduations sharing the same LT.

### Title
Concurrent graduations sharing the same LT reserve asset can misclassify escrowed funds as sweepable rebalance residue - (File: packages/contracts/src/Bonding.sol)

### Summary
The CVE's root cause is that two independently-lifecycled domains (DSI, CSI) share underlying control state (clock/reset bits) without proper ownership tracking, so one domain's teardown corrupts the other's still-active state. `Bonding.sol` has the same shape: multiple different launched `Token`s can be paired against the *same* BounceTech LT contract (nothing in `launch()` enforces LT uniqueness), so `Bonding`'s own LT balance is a shared pool across concurrently-graduating tokens, and the code explicitly acknowledges and attempts to firewall this via a `protectedLT` snapshot in `finalizeGraduation`.

### Finding Description
`finalizeGraduation` computes `protectedLT = ltBalance - p.ltFromPair` where `ltBalance` is `IERC20(lt).balanceOf(address(this))` — the *entire* LT balance held by the `Bonding` contract, not scoped per-token [1](#0-0) . The comment explicitly states this is meant to protect "a concurrent graduation on the same LT" from being swept as residue by `_sweepLTToOwner` [2](#0-1) .

This snapshot is taken **before** `_seedUniswapV2Direct` runs, which for a hostile-pre-seed (Regime 3) can pull in additional LT via `IUniswapV2Pair(pair).skim(address(this))` [3](#0-2) , and `_sweepLTToOwner` is called with `keep = protectedLT` fixed at the pre-seeding snapshot [4](#0-3) . If token A's `finalizeGraduation` executes while token B (sharing the same LT) is mid-way through its own phase-1→phase-2 window (its `ltFromPair` already transferred to `Bonding` via `Router.graduate` in `_prepareGraduationLiquidity`, `Bonding.sol:1084-1087`), token A's `protectedLT` calculation is a point-in-time snapshot of a balance that a third-party reentrant call, a differently-ordered concurrent finalize, or an LT with reentrant/callback semantics on `transfer`/`skim` could alter between the snapshot and the sweep. `_sweepLTToOwner` at the end unconditionally sweeps anything above `keep` to `owner()` [5](#0-4) .

### Impact Explanation
If the shared-LT accounting window can be forced out of sync — e.g., by permissionlessly calling `triggerGraduation`/driving a second token's `finalizeGraduation` into the same block/tx ordering, or via any LT whose `transfer` has reentrant hooks — another token's escrowed graduation LT (`ltFromPair` sitting in `Bonding` awaiting its own `finalizeGraduation`) can be swept to the protocol owner via `LTRescued`, permanently freezing that token's LP-seeding funds (its `finalizeGraduation` would then seed the pool with less LT than the curve actually raised, or brick entirely if the balance drops below what regime-1/3 math expects). This is a fund-freezing/misallocation bug matching "permanent freezing of trader, creator or LP funds."

### Likelihood Explanation
This requires two tokens deliberately launched against the same LT address (permissionless — any creator can pick an existing LT in `LaunchParams.ltAddress`, the only check is `ltExists` in `launch()`, `Bonding.sol:396-400`) and their graduations timed to overlap. The permissionless `triggerGraduation` and `finalizeGraduation` entry points make timing fully attacker-controlled by an unrelated wallet, no privileged role needed. However, exploiting the *snapshot staleness* specifically (vs. the already-documented and apparently-handled steady-state concurrent case) likely requires either reentrancy in the LT token or careful multi-tx ordering, which I could not fully verify against the actual BounceTech LT implementation (not in this repo) — so likelihood is dependent on external LT behavior I cannot confirm from `packages/contracts/src` alone.

### Recommendation
Track per-token escrowed LT explicitly (e.g., a `mapping(address token => uint256) escrowedLt` incremented in `_prepareGraduationLiquidity` and decremented in `finalizeGraduation`) instead of deriving `protectedLT` from a live `balanceOf` snapshot, and re-check the invariant immediately before `_sweepLTToOwner` rather than relying on a value captured before `_seedUniswapV2Direct` mutates the shared balance.

### Proof of Concept
1. Creator launches Token A with `LaunchParams.ltAddress = LT` via `Zap.createToken`/`Bonding.launch`.
2. A different creator launches Token B with the same `ltAddress = LT`.
3. Both curves are bought up to `canGraduate` (USD or sellout trigger) and enter `Lifecycle.Graduating`; `_prepareGraduationLiquidity` for both calls `router.graduate(token, ltFromPair)`, transferring both tokens' real LT into `Bonding`'s balance (`Bonding.sol:1084-1087`).
4. Any address calls `finalizeGraduation(tokenA)`. Before/around the `_sweepLTToOwner` call, if the LT contract's `transfer`/`skim` interaction (invoked inside `_seedUniswapV2Direct`, `Bonding.sol:1201-1234`) enables reentrancy or if Token B's `finalizeGraduation` is interleaved in the same block via a bundled transaction, Token A's stale `protectedLT` snapshot no longer reflects Token B's true escrow, and `_sweepLTToOwner` sends Token B's still-owed LT to `owner()`.
5. Token B's later `finalizeGraduation` seeds its LP with less LT than its curve actually raised, or reverts, freezing Token B's LP/creator value.

**Confidence caveat:** I could not execute this against the actual BounceTech LT contract (external, not in `packages/contracts/src`) to confirm reentrancy is actually reachable through `transfer`/`skim`; the finding is grounded in the documented shared-balance snapshot mechanism in `Bonding.sol` itself, but full exploitability depends on external LT behavior outside this repo's scope.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1007-1021)
```text
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

```

**File:** packages/contracts/src/Bonding.sol (L1022-1025)
```text
        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);
```

**File:** packages/contracts/src/Bonding.sol (L1042-1052)
```text
    function _sweepLTToOwner(
        address lt,
        uint256 keep
    ) internal {
        uint256 bal = IERC20(lt).balanceOf(address(this));
        if (bal <= keep) return;
        uint256 amount = bal - keep;
        address recipient = owner();
        IERC20(lt).safeTransfer(recipient, amount);
        emit LTRescued(lt, recipient, amount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1209-1215)
```text
        // Regime 2 — pull any donation pre-seed into this contract so it
        // doesn't pollute the post-swap ratio. Routed to `address(this)`
        // (NOT `lpLock`) so donated TOKEN can be burned and donated LT
        // can be swept to the owner via `_sweepLTToOwner` — `LPLock` has
        // no rescue path, so anything sent there is permanently stuck.
        // No-op on a freshly-created pair (balance == reserves == 0).
        IUniswapV2Pair(pair).skim(address(this));
```
