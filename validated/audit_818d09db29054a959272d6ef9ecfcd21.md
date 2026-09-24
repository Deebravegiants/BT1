## Analysis

alt.fun's own version of "ETH sent by users in error cannot be retrieved" is not about native ETH — the protocol never expects ETH at all (Zap deals in USDC, the curve reserve asset is an LT ERC20). The real analog is **a mis-sent leveraged-token (LT) ERC20 transfer directly to `Bonding`**, which has no owner-controlled rescue path and is explicitly *protected from* the one sweep mechanism that exists.

### Root cause

`Bonding.finalizeGraduation` computes: [1](#0-0) 

`protectedLT = ltBalance - p.ltFromPair` (saturating), and the only sweep function, `_sweepLTToOwner`, is deliberately restricted to `bal - keep` where `keep = protectedLT`: [2](#0-1) 

`protectedLT` is designed to shield two things from being swept: (a) another concurrent graduation's escrowed LT, and (b) "stray dust" — i.e., LT accidentally or mistakenly transferred straight to `Bonding` outside the normal `Router.graduate` escrow flow. This is confirmed by the natspec on `finalizeGraduation` and the "Per-graduation LT isolation" section of `AGENTS.md`, which explicitly calls out "Old residue or a misdirected transfer sitting in `Bonding`" as something `protectedLT` is designed to leave untouched: [3](#0-2) 

The consequence: any LT balance sent directly to `Bonding` by an unrelated trader (fat-fingered transfer, wrong-address paste, or simply calling `IERC20(lt).transfer(bondingAddress, amount)` instead of going through `Zap.buy`/`Zap.sell`) is *never* recoverable. It is permanently classified as `protectedLT` on every subsequent graduation for that LT and is therefore excluded from both the LP deposit (`_routerDepositAndDispose`, which caps `remLT` at `ltBal - protectedLT`) and the sweep (`_sweepLTToOwner`, which only forwards `bal - keep`). There is no `onlyOwner` rescue/withdraw function in `Bonding.sol` for LT balances — I confirmed the 9 `onlyOwner` gated functions in the contract are administrative (router/impl/global-storage management), none of which pulls out stray LT.

Contrast this with `FeeVault`, which *does* have exactly this kind of rescue: `sweepDonations()` permissionlessly forwards any USDC balance beyond tracked accruals to `feeTo`: [4](#0-3) 

`Bonding` has no equivalent for LT. The design intentionally treats "misdirected transfer" and "concurrent-graduation escrow" identically as `protectedLT`, so building a sweep for the former would risk draining the latter — the protocol chose safety over recoverability, at the cost of permanently freezing any LT sent to `Bonding` by mistake.

### Title
Leveraged tokens (LT) sent directly to `Bonding` by mistake are permanently unrecoverable — ([File: packages/contracts/src/Bonding.sol])

### Summary
An unprivileged trader who mistakenly sends LT ERC20 tokens directly to the `Bonding` contract address (instead of routing through `Zap`) permanently loses those funds. `Bonding`'s only LT-sweep mechanism, `_sweepLTToOwner`, explicitly excludes any balance classified as `protectedLT`, and stray/misdirected LT is by design folded into `protectedLT` on every future graduation involving that LT, forever protecting it from being moved anywhere — including to the owner.

### Finding Description
`finalizeGraduation` snapshots `protectedLT = ltBalance - p.ltFromPair` at its top [5](#0-4) . This value is intended to shield concurrent-graduation escrow and "stray dust." It is passed into `_seedUniswapV2Direct` → `_routerDepositAndDispose`, which caps the LP deposit at `ltBal - protectedLT` [6](#0-5) , and into `_sweepLTToOwner`, which only transfers `bal - keep` where `keep = protectedLT` [7](#0-6) . Since `protectedLT` is a floor rather than a one-time snapshot cleared after use, any LT balance sitting in `Bonding` that isn't earmarked by the *current* graduation's `ltFromPair` is preserved on every subsequent graduation touching that LT, indefinitely. There is no admin or permissionless function anywhere in `Bonding.sol` that can withdraw this residual balance.

### Impact Explanation
This is a permanent freezing of trader funds: LT tokens (a real, valuable ERC20 reserve asset representing leveraged BounceTech exposure) sent to `Bonding` by error can never be retrieved by the sender, the protocol owner, or anyone else. Given the AGENTS.md documentation explicitly anticipates "misdirected transfers" as a real scenario that `protectedLT` must defend against (rather than something impossible to occur), this is a foreseeable and unrecoverable loss of user funds — qualifying as Medium severity permanent freezing of funds, matching the impact class of the original report.

### Likelihood Explanation
Likelihood is driven purely by ordinary user error: any wallet interacting with the LT token contract could mistype/paste the `Bonding` proxy address instead of `Zap`'s, especially since `Bonding` and `Zap` are both protocol-facing UUPS proxies likely bookmarked or copy-pasted by users/integrators. No attacker action or privileged role is required — a single unprivileged `IERC20(lt).transfer(bondingAddress, amount)` call is sufficient to trigger the permanent loss.

### Recommendation
Add an owner-gated (or time-delayed/permissionless-after-cooldown) rescue function on `Bonding` that allows sweeping LT balance that has remained `protectedLT` for longer than any plausible concurrent-graduation window (e.g., no pending graduation exists for that LT and the balance has been stable across N blocks), or track per-LT "escrowed" amounts explicitly (rather than inferring via subtraction) so genuine stray transfers can be distinguished from legitimate escrow and safely swept to the owner, mirroring `FeeVault.sweepDonations()`.

### Proof of Concept
1. A trader intending to interact with `Zap.sell`/`Zap.buy` instead calls `IERC20(lt).transfer(address(bonding), 100e18)` directly (e.g., wallet address-book mix-up between `Bonding` and `Zap` proxy addresses).
2. `Bonding` now holds `100e18` LT with no `pendingGraduation` referencing it.
3. On the next `finalizeGraduation` call for *any* token paired with that same LT, `protectedLT = ltBalance - p.ltFromPair` includes the stray `100e18` [8](#0-7) .
4. `_routerDepositAndDispose` excludes it from the LP deposit, and `_sweepLTToOwner` excludes it from the sweep-to-owner (`keep = protectedLT`) [9](#0-8) .
5. The `100e18` LT remains in `Bonding` after this and every future graduation on the same LT, with no function anywhere in `Bonding.sol` capable of extracting it — permanently frozen.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1010-1025)
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

        _sweepLTToOwner(lt, protectedLT);
```

**File:** packages/contracts/src/Bonding.sol (L1036-1052)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1449-1473)
```text
    function _routerDepositAndDispose(
        address tokenAddress,
        address lt,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        BondingStorage storage $ = _s();
        address routerAddr = $.uniswapV2Router;
        address lpLock_ = $.lpLock;
        uint256 remToken = IERC20(tokenAddress).balanceOf(address(this));
        // Subtract `protectedLT` (LT that doesn't belong to this graduation
        // — concurrent escrows or stray dust, snapshotted at the top of
        // `finalizeGraduation`) so the deposit allowance can never pull
        // another graduation's earmark or accidentally absorb dust into a
        // locked LP.
        uint256 ltBal = IERC20(lt).balanceOf(address(this));
        uint256 remLT = ltBal > protectedLT ? ltBal - protectedLT : 0;

        if (remToken > 0 && remLT > 0) {
            IERC20(tokenAddress).forceApprove(routerAddr, remToken);
            IERC20(lt).forceApprove(routerAddr, remLT);
            (,, liquidity) = IUniswapV2Router02(routerAddr)
                .addLiquidity(tokenAddress, lt, remToken, remLT, 1, 1, lpLock_, block.timestamp);
            IERC20(tokenAddress).forceApprove(routerAddr, 0);
            IERC20(lt).forceApprove(routerAddr, 0);
        }
```

**File:** packages/contracts/AGENTS.md (L210-219)
```markdown
### Per-graduation LT isolation

`finalizeGraduation` snapshots `protectedLT = balanceOf(this) - p.ltFromPair` at the top: any LT in `Bonding` beyond this graduation's earmark is either another concurrent graduation's escrow (Phase 1 already moved it in via `Router.graduate`) or stray dust. Both must stay out of THIS graduation's LP and post-sweep.

That snapshot is plumbed through `_seedUniswapV2Direct` → `_seedRebalancing` → `_routerDepositAndDispose`, where the deposit allowance is capped at `balanceOf(this) - protectedLT`. Then a single `_sweepLTToOwner(lt, protectedLT)` at the end of `finalizeGraduation` sends only THIS graduation's rebalance residue to the protocol owner, leaving any concurrent-graduation escrow / stray dust untouched. Honest empty-pair graduations have no residue at the post-sweep so it's a no-op there.

Two scenarios this guards against:

- **Concurrent graduations on the same LT.** Two tokens A and B share an LT and both reach `Lifecycle.Graduating` before either finalizes (the keeper takes ~60s and popular LTs see overlap). Without `protectedLT`, A's finalize would treat the full balance as its own and either sweep B's escrow to the owner (bricking B's later finalize) or — for hostile-pre-seed graduations — deposit it into A's locked LP. With it, A only ever sees `ltFromPair_A` and B is preserved.
- **Cross-token LT residue.** Old residue or a misdirected transfer sitting in `Bonding` would otherwise be visible to `_routerDepositAndDispose`'s `balanceOf(this)` read and could be silently consumed into a future graduation's locked LP. With `protectedLT`, contamination stays in `Bonding` and the deposit only sees this graduation's earmark.
```

**File:** packages/contracts/src/FeeVault.sol (L147-160)
```text
    /// @notice Sweep unbacked USDC (donations) to `feeTo`. Required because
    ///         direct USDC transfers would otherwise inflate `balanceOf` above
    ///         the accrual tally and silently mask the `accrue` underfund
    ///         check. Permissionless — funds always go to the admin-set `feeTo`.
    function sweepDonations() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        uint256 backed = $.totalAccruedCreator + $.protocolBalance;
        uint256 balance = $.usdc.balanceOf(address(this));
        if (balance <= backed) revert NothingToClaim();
        amount = balance - backed;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit DonationsSwept(feeTo_, amount);
    }
```
