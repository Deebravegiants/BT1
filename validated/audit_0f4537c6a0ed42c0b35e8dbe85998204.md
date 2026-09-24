### Title
Stray LT donated directly to `Bonding` is permanently unrecoverable unless a graduation on the same LT happens to occur afterward - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding`'s only mechanism for recovering LT tokens that end up sitting in the contract (e.g. from a direct/accidental transfer, or cross-token residue) is `_sweepLTToOwner`, which is invoked exclusively from inside `finalizeGraduation` [1](#0-0) . There is no standalone, permissionless, or owner-only function to sweep LT balances held by `Bonding` outside of a graduation flow. If a wallet transfers LT directly into `Bonding` for a token/LT pair that is not concurrently in `Lifecycle.Graduating`, and no other token sharing that LT ever reaches graduation afterward, that LT is permanently stuck — mirroring the Sherlock finding where `Stream.rescueERC20` can never reach the payment token even after the stream's funds have been fully settled.

### Finding Description
`finalizeGraduation` computes `protectedLT = balanceOf(this) - p.ltFromPair` (saturating at 0) and, after seeding the LP, calls `_sweepLTToOwner(lt, protectedLT)`, which transfers `balanceOf(this) - protectedLT` (i.e., any residue beyond the current graduation's earmark) to the owner and emits `LTRescued` [1](#0-0) . This is documented as intentional: `finalizeGraduation` snapshots `protectedLT` so that stray dust or a concurrent graduation's escrow is not consumed by *this* graduation's LP/deposit, and any true residue is auto-swept to the owner at the end [2](#0-1) .

The critical gap is that this sweep path is **conditioned entirely on some token paired with that LT reaching `finalizeGraduation`**. `_sweepLTToOwner` is a private helper called only once, at the tail of `finalizeGraduation`; there is no analog of `rescueERC20` on `Bonding` that can be invoked independently by the owner or anyone else to recover LT balances that are not tied to an active `pendingGraduation` entry. If:
- an unrelated wallet transfers LT directly to the `Bonding` contract address (a reachable, unprivileged action — direct ERC20 transfer of an LT into `Bonding`), and
- no bonding curve paired with that specific LT is currently `Graduating`, and no such curve ever later triggers `finalizeGraduation` on that LT (e.g., the LT is a low-traffic/one-off pairing, or all curves on that LT have already graduated),

then that LT balance sits in `Bonding` indefinitely with no code path that can ever move it out. This is structurally the same bug class as the Sherlock `Stream.rescueERC20` finding: a rescue mechanism exists, but it is gated on an unrelated lifecycle event (there, the stream must not yet have ended and the token must not equal the payment token; here, some future graduation on the exact same LT must occur) rather than being callable independently whenever a genuine surplus exists.

### Impact Explanation
Any LT sent to `Bonding` outside the narrow window of an active graduation on that same LT is permanently frozen with no on-chain recovery path — a direct freezing of funds belonging to whoever sent them (and, since the design intends for this residue to go to the protocol owner via `LTRescued`, it also represents a permanent loss of expected protocol revenue in that scenario). This satisfies the "permanent freezing of trader/creator/LP funds" bar for a valid finding, though the loss is scoped to accidental/incidental LT transfers into `Bonding` rather than the curve's own operational funds (curve-raised LT is drained via `Router.graduate` and is not exposed to this gap).

### Likelihood Explanation
Likelihood is data-dependent: it requires (a) an LT balance landing in `Bonding` outside the `ltFromPair` accounting for an active graduation, and (b) no future graduation ever occurring on that exact LT to trigger the sweep. Because many distinct BounceTech LTs can be used as reserve assets across many tokens, and because a given LT might only ever back a single bonding curve that either never graduates or has already graduated, this is a realistic (not purely theoretical) scenario — any direct/mistaken LT transfer to `Bonding`'s address for such an LT is stuck from the moment it lands.

### Recommendation
Add a standalone rescue function on `Bonding`, callable by the owner (or permissionlessly, paying out to the fixed owner address as `FeeVault.sweepDonations` does), that computes and sweeps only the LT balance in excess of the sum of all currently pending graduations' `ltFromPair` amounts for that LT — i.e., generalize `protectedLT` accounting to be tracked globally per-LT (not just within a single `finalizeGraduation` call) so genuine surplus LT can be recovered at any time, not only as a side effect of some future graduation completing.

### Proof of Concept
1. Launch a token `T1` against LT `L1` via `Zap.createToken`; do not trade it to graduation.
2. An unrelated wallet calls `L1.transfer(address(bonding), amount)` — a plain ERC20 transfer, fully permissionless.
3. `T1` never reaches the USD or supply graduation trigger (e.g., trading stalls, or `T1` is later abandoned) and no other token is ever launched against `L1`.
4. `bonding.finalizeGraduation` is never invoked for any token paired with `L1`, so `_sweepLTToOwner` never runs for `L1`.
5. The `amount` of `L1` held by `Bonding` from step 2 remains in the contract permanently — there is no other function in `Bonding.sol` that transfers out LT balances [3](#0-2) .

Note: I was not able to review the complete `Bonding.sol` file end-to-end (only the sections returned by search/read tools) to exhaustively confirm no other rescue entry point exists; if the codebase has additional admin functions elsewhere in the file not surfaced by my searches, they should be checked before treating this as conclusively unmitigated. Given index size limits, starting a full Devin session to grep the entire file for every `external`/`onlyOwner` function would give complete certainty.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1052)
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

    /// @dev Send LT held by this contract above `keep` to the owner,
    ///      emitting `LTRescued`. Called at the end of
    ///      `finalizeGraduation` with `keep = protectedLT` (any escrow
    ///      that doesn't belong to this graduation), so only THIS
    ///      graduation's rebalance residue lands on the owner. No-op on
    ///      the empty-pair fast path (nothing to sweep).
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

**File:** packages/contracts/AGENTS.md (L211-221)
```markdown

`finalizeGraduation` snapshots `protectedLT = balanceOf(this) - p.ltFromPair` at the top: any LT in `Bonding` beyond this graduation's earmark is either another concurrent graduation's escrow (Phase 1 already moved it in via `Router.graduate`) or stray dust. Both must stay out of THIS graduation's LP and post-sweep.

That snapshot is plumbed through `_seedUniswapV2Direct` → `_seedRebalancing` → `_routerDepositAndDispose`, where the deposit allowance is capped at `balanceOf(this) - protectedLT`. Then a single `_sweepLTToOwner(lt, protectedLT)` at the end of `finalizeGraduation` sends only THIS graduation's rebalance residue to the protocol owner, leaving any concurrent-graduation escrow / stray dust untouched. Honest empty-pair graduations have no residue at the post-sweep so it's a no-op there.

Two scenarios this guards against:

- **Concurrent graduations on the same LT.** Two tokens A and B share an LT and both reach `Lifecycle.Graduating` before either finalizes (the keeper takes ~60s and popular LTs see overlap). Without `protectedLT`, A's finalize would treat the full balance as its own and either sweep B's escrow to the owner (bricking B's later finalize) or — for hostile-pre-seed graduations — deposit it into A's locked LP. With it, A only ever sees `ltFromPair_A` and B is preserved.
- **Cross-token LT residue.** Old residue or a misdirected transfer sitting in `Bonding` would otherwise be visible to `_routerDepositAndDispose`'s `balanceOf(this)` read and could be silently consumed into a future graduation's locked LP. With `protectedLT`, contamination stays in `Bonding` and the deposit only sees this graduation's earmark.

The auto-sweep emits `LTRescued(lt, owner, amount)` for indexer observability. The dedicated regression tests for these edge cases were removed alongside `HostilePreSeed.t.sol`; future changes to `finalizeGraduation` / `_routerDepositAndDispose` / `_sweepLTToOwner` should add targeted coverage if the behaviour is non-obvious from the unit-level tests in `TwoPhaseGraduation.t.sol`.
```
