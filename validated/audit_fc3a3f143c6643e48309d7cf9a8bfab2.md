### Title
Direct LT transfers to `Bonding` are never freed — no sweep or rescue path exists outside a live graduation's `protectedLT` accounting - ([File: packages/contracts/src/Bonding.sol])

### Summary
This is the closest reachable analog to CVE-2021-47231's bug class: a resource is transferred into a contract's custody but the code that is supposed to free/reclaim it only runs on one narrow, specific code path (`finalizeGraduation`'s `_sweepLTToOwner`), and any LT balance that doesn't fall inside that path's specific accounting is permanently retained with no cleanup function ever reachable for it — analogous to the `mcba_usb` coherent buffers that were only freed on the resubmit path and never released on disconnect.

### Finding Description
`finalizeGraduation` computes `protectedLT` at the top of the function as "any LT balance beyond `p.ltFromPair` belongs to a concurrent graduation or is stray dust" and deliberately preserves it rather than sweeping it: [1](#0-0) 

`_sweepLTToOwner` only sweeps the balance above `keep` (`protectedLT`), and is only ever invoked from `finalizeGraduation` for the specific `lt` tied to the token currently being finalized: [2](#0-1) 

Because `protectedLT` is computed purely as "balance minus THIS token's `ltFromPair`" (which itself is derived only from the pair's own reserves, per `_prepareGraduationLiquidity`/`_launchTimeVirtualLtReserve`, not from Bonding's balance), any LT that lands on the `Bonding` contract by a direct `IERC20(lt).transfer(bonding, amount)` call — unconnected to any pair's `ltFromPair` accounting — is classified as "protected" on every single future `finalizeGraduation` call for every token that shares that LT, forever. It is never counted as anyone's own earmark, so it is never swept, never deposited into any LP, and never burned.

Unlike `FeeVault`, which explicitly ships a permissionless `sweepDonations()` to reclaim unbacked USDC sent directly to the vault: [3](#0-2) 

`Bonding.sol` has no equivalent function. I searched for `rescue`/`sweep`/`recoverToken`/`onlyOwner` in `Bonding.sol` and found no owner-only or permissionless rescue path for arbitrary/stray LT balances sitting in the contract outside the graduation flow. The only cleanup mechanism (`_sweepLTToOwner`) is gated behind a live `finalizeGraduation(tokenAddress)` call for a token using that specific LT, and even then it explicitly excludes anything not tied to `p.ltFromPair` for that call.

### Impact Explanation
Any unprivileged wallet that sends LT directly to the `Bonding` contract address (accidentally, via a wrong-target transfer, or via any other on-chain flow that ends up moving LT there outside the graduation lifecycle) permanently loses that LT. There is no owner, keeper, or permissionless function anywhere in the reachable contract set that can ever recover it — it sits in `Bonding`'s balance and is defensively excluded from every subsequent `finalizeGraduation`'s sweep and LP-deposit accounting by design (`protectedLT`). This is a permanent freezing of funds with no recovery path, matching the "unfreed resource" bug class of the CVE, mapped onto alt.fun's own LT-holding contract (`Bonding`) rather than the kernel USB buffer.

### Likelihood Explanation
Reachable by any unprivileged address with nothing more than a standard ERC20 `transfer` call against the LT contract, targeting `Bonding`'s address — no privileged role, no timing dependency, and no interaction with `Zap`/`Pair`/`Router` needed. The likelihood of *accidental* transfers is realistic (users mis-target contract addresses regularly in DeFi), and the permanence of the loss (impossible-to-recover-ever) is a design gap rather than a one-off edge case, since `protectedLT`'s definition structurally guarantees any non-earmarked LT is excluded from every future sweep.

### Recommendation
Add a permissionless (or owner-gated, paid out to a fixed recipient like `FeeVault.sweepDonations()`'s `feeTo` pattern) sweep function on `Bonding` for each supported LT, computed the same way `FeeVault.sweepDonations()` computes surplus: `balance - sum(all outstanding `ltFromPair` earmarks for pending graduations on that LT)`. This mirrors the exact pattern already proven safe in `FeeVault` and closes the permanent-freeze gap without weakening `protectedLT`'s concurrent-graduation isolation guarantee.

### Proof of Concept
1. Any address (unprivileged) calls `IERC20(lt).transfer(address(bonding), X)` directly against the LT contract, sending `X` LT tokens to `Bonding`'s address. This requires only holding LT and calling a standard ERC20 `transfer` — no interaction with any alt.fun contract function is needed.
2. This LT is now part of `Bonding`'s balance but is not associated with any token's `pendingGraduation[token].ltFromPair`.
3. On every subsequent `finalizeGraduation(anyToken)` call for any token sharing that LT, `protectedLT = ltBalance - p.ltFromPair` includes `X` as "protected" (concurrent/dust) and `_sweepLTToOwner` explicitly skips it (`if (bal <= keep) return;`), per [4](#0-3) .
4. `X` remains in `Bonding`'s balance indefinitely across every future graduation cycle. There is no function in `Bonding.sol` — permissionless or owner-only — that can ever extract it, unlike `FeeVault.sweepDonations()` which exists for exactly this class of stray-balance problem in a sibling contract, per [3](#0-2) .

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
