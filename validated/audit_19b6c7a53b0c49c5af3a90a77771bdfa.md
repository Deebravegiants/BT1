### Title
Direct LT donations to an active curve `Pair` are permanently unrecoverable after graduation — ([File: packages/contracts/src/Router.sol], [File: packages/contracts/src/Pair.sol], [File: packages/contracts/src/Bonding.sol])

### Summary
Any unprivileged wallet or trader who sends the reserve LT asset directly to a bonding-curve `Pair` (a plain ERC20 `transfer`, not via `Zap`/`Bonding`) creates a balance that exceeds the pair's stored `assetReserve`. The protocol deliberately excludes this "donated" LT from graduation's LT drain and from LP seeding, and the only function capable of moving LT out of a `Pair` (`Pair.transferAsset`, gated `onlyRouter`) is invoked exclusively by `Router.graduate`, which `Bonding` calls exactly once, from `_prepareGraduationLiquidity`, before the token's lifecycle flips past `Curve`. Once the token is `Graduating`/`Graduated`, this call path is permanently unreachable, so any donated LT sitting in the `Pair` is permanently frozen with no owner-, keeper-, or user-callable rescue path — closely analogous to the Hegic incident where 152.2 ETH of unexercised-option value became permanently locked in the contract with no protocol-level recovery mechanism.

### Finding Description
`Pair.transferAsset` can only be called by `router` [1](#0-0) . `Router` exposes this via exactly two paths: `Router.sell` (bounded by `_computeSell`'s curve math) and `Router.graduate`, both gated by `BONDING_ROLE` [2](#0-1) . `Router.graduate` transfers only an explicit `amount` passed by the caller — never the pair's live `assetBalance()` — specifically so that LT donated directly to the pair via `IERC20.transfer` is excluded and left behind [3](#0-2) .

`Bonding` calls `Router.graduate(token, ltFromPair)` exactly once, inside `_prepareGraduationLiquidity` (invoked from `_enterGraduating`, phase 1 of graduation), draining only `ltFromPair = storedAssetReserve - virtualLtReserve` — never the donated excess [4](#0-3) . After `_enterGraduating` runs, the token's lifecycle is `Graduating`, and `finalizeGraduation` requires `lifecycle == Graduating` and flips it to `Graduated` [5](#0-4) ; `triggerGraduation` explicitly reverts once already `Graduating` or past `Curve` [6](#0-5) . There is no other function in `Bonding` that calls `Router.graduate` a second time for the same token — the docs and Router's own natspec confirm this is a deliberate, permanent one-shot: *"Bonding in turn only calls graduate from _prepareGraduationLiquidity — which is unreachable once the token's lifecycle has flipped past Curve... the leftover is unreachable"* [7](#0-6) . This is corroborated by the spec's own invariant table: *"assetBalance() == 0 only when no donations occurred — any LT donated directly to the pair is excluded from LP seeding and remains locked in the pair"* [8](#0-7) .

Since `BONDING_ROLE` on `Router` is the only gate on `Pair.transferAsset` and `Bonding` never grants itself a second graduate call, any LT sent directly to the `Pair` address — by mistake (e.g. a user confusing the pair address with `Zap`) or intentionally (e.g. to test donation-resistance, or as a griefing/self-harm action) — becomes permanently stuck in the `Pair` contract once that token graduates, with **zero on-chain path to retrieve it**, for creators, traders, or the protocol owner alike.

### Impact Explanation
This is a permanent freezing of funds bug class, directly analogous to the referenced Hegic incident (funds permanently locked in a contract with no built-in on-chain recovery, requiring an off-chain, ad-hoc remediation). Here, any LT reserve asset transferred directly into a `Pair` — reachable by any unprivileged address via a plain ERC20 `transfer` call, a path explicitly listed as in-scope — is unrecoverable on-chain after the pair graduates. Given LTs represent real leveraged USD-value assets, this constitutes concrete permanent freezing of trader/creator funds, satisfying the "Validate" criterion for permanent freezing of funds.

### Likelihood Explanation
No privilege is required: any address holding the paired LT can call `IERC20(lt).transfer(pairAddr, amount)` at any point while the token is still on the `Curve` lifecycle. Graduation is a normal, expected event (triggered by ordinary buys/sells or `triggerGraduation`), so any donation that lands before graduation is guaranteed to become permanently stranded the moment the token transitions `Curve → Graduating → Graduated`. The likelihood of an accidental donation (e.g., a user sending LT to the wrong address, mistaking the Pair for the Zap contract) is realistic given LTs and Pair addresses are both plain ERC20-compatible contracts a user might interact with directly.

### Recommendation
Add a permissionless or owner-gated sweep/rescue function reachable after graduation that allows any LT held by a graduated `Pair` beyond its accounted reserves to be recovered (e.g., mirroring `Bonding._sweepLTToOwner`'s pattern used for hostile-pre-seed residue) — for example, a one-time post-graduation `Router`/`Bonding` call that reads `Pair.assetBalance()` and drains any excess over the last recorded `assetReserve` to a designated recipient (protocol owner, or better, held for the token's creator/community to claim), rather than leaving it permanently trapped behind a role that can never call `Pair.transferAsset` again for that token.

### Proof of Concept
1. `Bonding.launch(...)` a token; a trader/creator does normal buys via `Zap.buy` until the token is close to, but not yet at, graduation.
2. An unprivileged wallet calls `IERC20(ltAddress).transfer(pairAddr, X)` directly against the `Pair` contract (bypassing `Zap`/`Bonding` entirely) — this is a plain, permissionless ERC20 transfer that only requires knowing the `Pair` address, obtainable from `Bonding.tokenInfo(token).pair`.
3. Trading continues; eventually a buy crosses the USD/supply threshold and `Bonding._executeBuy` calls `_enterGraduating`, which calls `_prepareGraduationLiquidity` → `Router.graduate(token, ltFromPair)`. `ltFromPair` is computed from the stored `assetReserve`, so it excludes the donated `X` per the "donation resistance" design [4](#0-3) .
4. `finalizeGraduation` seeds the HyperSwap LP and flips lifecycle to `Graduated` [5](#0-4) .
5. Confirm `IPair(pairAddr).assetBalance() == X` (nonzero) while `bonding.isGraduated(token) == true`. Attempt every external call that could move LT out of `pairAddr`: `Router.graduate` reverts with `TokenIsGraduating`/`NotGraduating`-equivalent state on `Bonding`'s side (unreachable — no function calls it again), and direct `Pair.transferAsset` reverts `OnlyRouter` for any non-router caller, and `Router.sell`/`buy` are also `BONDING_ROLE`-gated and internally bounded by the curve math (not `assetBalance()`), so `X` can never be extracted. This can be observed directly against the existing `test/GraduationInvariants.t.sol` "Donation resistance" test comment, which documents `assetBalance() == 0 only when no donations occurred` [8](#0-7)  — i.e., the donated LT is confirmed by the project's own test suite to remain in the pair indefinitely.

### Citations

**File:** packages/contracts/src/Pair.sol (L81-86)
```text
    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }
```

**File:** packages/contracts/src/Router.sol (L150-211)
```text
    /// @notice Tokens in → LT out.
    function sell(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 tokensIn, uint256 assetOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        tokensIn = amountIn;

        IERC20(token).safeTransferFrom(to, pairAddr, amountIn);

        assetOut = _computeSell(pairAddr, amountIn);

        IPair(pairAddr).transferAsset(to, assetOut);

        IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
    }

    function _computeSell(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 assetOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        uint256 newReserveToken = reserveToken + amountIn;
        assetOut = reserveAsset - (k / newReserveToken);
    }

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

**File:** packages/contracts/src/Bonding.sol (L1054-1073)
```text
    /// @dev Burns unsold curve tokens, drains real raised LT, computes
    ///      `tokensForLP` for zero-gap LP seeding, burns the LP excess.
    ///
    ///      Price equality: `tokensForLP / ltFromPair = tokenReserve / assetReserve`,
    ///      with `ltFromPair = assetReserve - virtualLtReserve` (the LT
    ///      actually raised by the curve, excluding the launch-time virtual
    ///      seed; the seed is recovered as `Pair.k() / TOTAL_SUPPLY`, see
    ///      `_launchTimeVirtualLtReserve`). Substituting gives LP price =
    ///      `assetReserve / tokenReserve` = curve close marginal price.
    ///      Donations of LT directly to the pair don't move the stored
    ///      `assetReserve`, so they're excluded from `ltFromPair`.
    ///
    ///      Token-side donations are handled by `unsoldBurned`: any tokens
    ///      sitting in the pair beyond the curve's accounting are burned.
    ///
    ///      With virtual `tokenReserve = totalSupply` and `curveSupply = 75%`,
    ///      the parabola `tokensForLP(sold) = sold·(S−sold)/S` peaks at
    ///      `S/4 = LP_RESERVE` when `sold = S/2`, so `tokensForLP ≤ LP_RESERVE`
    ///      is mathematically invariant. The cap is defensive.
    function _prepareGraduationLiquidity(
```

**File:** docs/contracts-scope.md (L103-107)
```markdown
| 4 | Pair drained | `tokenBalance() == 0` post-graduation. `assetBalance() == 0` only when no donations occurred — any LT donated directly to the pair is excluded from LP seeding and remains locked in the pair. |
| 5 | Both triggers work | Supply trigger fires below `$9K`; USD trigger fires with supply remaining |
| 6 | Overflow refund | Oversized buys charge only `amountInUsed`, not requested amount |
| 7 | Donation resistance | Direct LT donations to the pair don't trigger graduation and don't skew LP open price; donated LT stays locked in the curve pair |

```
