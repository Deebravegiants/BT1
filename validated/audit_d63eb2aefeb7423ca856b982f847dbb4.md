This CVE-2022-22590 is a WebKit/Safari use-after-free in memory management triggered by malicious web content — a C++ heap-object lifetime bug. That bug class has no meaningful analog in this codebase: Solidity has no manual memory management, pointers, or object lifetimes that can be freed and later dereferenced. There is no mechanism in `packages/contracts/src` where a storage/memory reference is "freed" and then reused stale within the same call in a way that mirrors a UAF.

I checked the areas most likely to exhibit a UAF-shaped bug (stale cached references reused after being deleted/reset):

- `Bonding.finalizeGraduation` deletes `$.pendingGraduation[tokenAddress]` and updates `info.lifecycle` in a fixed order, guarded by `nonReentrant`, with `LPLock.recordLock` called last and gated by a one-shot `lockedAt` sentinel that reverts on a second call (`AlreadyLocked`). [1](#0-0) [2](#0-1) 
- `FeeVault.claim` / `claimProtocol` / `sweepDonations` zero out the relevant balance *before* the external `safeTransfer`, and are further protected by `ReentrancyGuard`, so there's no stale-balance-reuse path; this is explicitly tested against a reentrant USDC mock. [3](#0-2) [4](#0-3) 
- `Bonding.triggerGraduation` / phase-1/phase-2 graduation split is permissionless but state-gated by `Lifecycle` enum checks (`TokenIsGraduating`, `NotGraduating`) that prevent any double-entry or stale-state reuse across the two-phase split. [5](#0-4) 

None of these present a genuine "stale reference reused after invalidation" pattern that would map to a use-after-free, and none of the documented accepted-risk design choices (dust pre-seeding, cross-tx drift, add-only locker allowlist) rise to a concrete theft/freezing bug of the kind required by the validation criteria — they are explicitly reasoned-through, intentional tradeoffs in `packages/contracts/AGENTS.md`. [6](#0-5) 

Given this, forcing a "UAF analog" onto this contract set would require fabricating a root cause that isn't actually present in the code.

#No Vulnerability found for this question.

### Citations

**File:** packages/contracts/src/Bonding.sol (L970-1034)
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

    /// @notice Phase 2: seed the V2 LP and lock it. Permissionless —
    ///         keeper drives the happy path; anyone can rescue a stuck token.
    /// @dev Bypasses the V2 router and calls `pair.mint(lpLock)`
    ///      directly. This is brick-proof against a front-runner pre-creating
    ///      the pair and dust-seeding it between phases.
    /// @dev Exchange-rate drift between phase 1 and phase 2 is accepted by
    ///      design. The cached `(tokensForLP, ltFromPair)` are pure pair-
    ///      state arithmetic — see `_prepareGraduationLiquidity`, which
    ///      never reads `exchangeRate()` — so the LP opens at the exact
    ///      LT-per-token ratio the curve closed at, regardless of how long
    ///      phase 2 takes. What drifts is only the USD denomination of the
    ///      LT side, which is inherent to using a leveraged token as the
    ///      curve reserve: holders accept that exposure when they buy in.
    ///      A keeper Worker drives finalize within ~60s of `TokenGraduating`,
    ///      so the practical drift window is single-digit seconds. No
    ///      freshness timestamp / staleness gate: a recompute would return
    ///      byte-identical values (inputs are frozen while
    ///      `Lifecycle.Graduating`), and re-pricing the LP at the live
    ///      `exchangeRate()` would break the zero-gap-in-LT-units invariant.
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

**File:** packages/contracts/src/LPLock.sol (L69-85)
```text
    /// @notice Record an LP lock. LP tokens must already sit at this address.
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

**File:** packages/contracts/src/FeeVault.sol (L127-160)
```text
    function claim() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.creatorBalance[msg.sender];
        if (amount == 0) revert NothingToClaim();
        $.creatorBalance[msg.sender] = 0;
        $.totalAccruedCreator -= amount;
        $.usdc.safeTransfer(msg.sender, amount);
        emit CreatorFeesClaimed(msg.sender, amount);
    }

    function claimProtocol() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.protocolBalance;
        if (amount == 0) revert NothingToClaim();
        $.protocolBalance = 0;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit ProtocolFeesClaimed(feeTo_, amount);
    }

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

**File:** packages/contracts/test/FeeVault.t.sol (L9-37)
```text
/// @dev ERC20 that triggers a reentrancy attempt on every transfer. Used to
///      confirm `FeeVault.claim` is protected by `ReentrancyGuard`.
contract ReentrantUsdc is MockERC20 {
    FeeVault public vault;
    bool private _attacking;

    constructor() MockERC20("USD Coin", "USDC") {}

    function setVault(
        FeeVault vault_
    ) external {
        vault = vault_;
    }

    function _update(
        address from,
        address to,
        uint256 value
    ) internal override {
        super._update(from, to, value);
        if (_attacking || address(vault) == address(0)) return;
        if (from == address(vault)) {
            _attacking = true;
            // Re-enter claim — should revert with ReentrancyGuardReentrantCall.
            try vault.claim() {} catch {}
            _attacking = false;
        }
    }
}
```

**File:** packages/contracts/AGENTS.md (L79-93)
```markdown
## Graduation — Two-Phase, Dynamic LP Seeding (Read This Before Touching Graduation Code)

This is the most bespoke piece of the protocol. Full rationale + invariants live in [`docs/contracts-scope.md`](../../docs/contracts-scope.md#graduation); the short version:

- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
- **Virtual token reserve.** At launch, `Pair.reserve0 = totalSupply (1B)` while only `curveSupply = 75%` (750M) of real tokens are transferred to the pair. The other 250M (`LP_RESERVE`) sit in `Bonding` for graduation. This extends the curve beyond the sellable supply, which is what makes dynamic LP seeding work cleanly.
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
- **Zero-gap LP seeding.** `_prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` (the real LT raised by the curve, donation-immune; `virtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`) and `tokensForLP = ltFromPair × storedTokenReserve / storedAssetReserve` at end-of-phase-1, caching the result. Phase 2 uses the cached value verbatim, so the curve→LP price match is invariant under the tx split. Donated LT stays in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation.
- **Parabola invariant.** With `V_t_init = totalSupply` and `curveSupply = 75%`, the function `tokensForLP(sold) = sold·(S−sold)/S` peaks at `S/4 = LP_RESERVE`. The cap in `_prepareGraduationLiquidity` is defensive — it can never bind in normal operation.
- **Overflow buy cap.** `Router.buy` caps `tokensOut` at the pair's real balance and back-calculates the LT consumed, so the last buy cannot exceed remaining supply. `Zap.buy` returns the unused LT (`ltMinted - amountInUsed`) directly as LT — not redeemed, to avoid re-incurring the LT redemption fee on dust — while unconverted USDC and the fee over-charge are refunded in USDC. `Bonding.buy` returns `(tokensOut, amountInUsed)` for this reason.

**If you change `_enterGraduating`, `finalizeGraduation`, `_prepareGraduationLiquidity`, `_seedUniswapV2Direct` (or any of its `_seedRebalancing` / `_pairRebalance` / `_routerDepositAndDispose` / `_noFeeSwapInput` helpers), `Router.buy`'s capping logic, or the seeding in `_deployAndSeed`:** you MUST re-run `test/GraduationInvariants.t.sol`, `test/TwoPhaseGraduation.t.sol`, and `test/NoFeeSwapInput.t.sol`. All 7 zero-gap invariants must still pass; the phase-1-fits-in-small-block budget assertion (1.8M) must still hold; the brick-resistance regression test must still pass. These invariants are the product — do not loosen their assertions to make a change go green.
```
