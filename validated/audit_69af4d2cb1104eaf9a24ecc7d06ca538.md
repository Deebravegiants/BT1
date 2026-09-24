I have enough to write the final answer. The strongest analog is LT donated directly to the curve `Pair` before/during the curve phase: `Router.graduate` and `Router.sell` are the only two functions that can move LT out of `Pair` (via `Pair.transferAsset`, `onlyRouter`), and both compute an exact, donation-excluding amount, so any LT sent to the `Pair` via a plain `IERC20.transfer` is permanently stranded there — unlike `FeeVault` (which has `sweepDonations()`) or `Bonding` (which has `_sweepLTToOwner`), `Pair` has no equivalent recovery path.

### Title
Permanently unrecoverable LT donated directly to the bonding-curve `Pair` - ([File: packages/contracts/src/Pair.sol])

### Summary
Any unrelated wallet can send LT directly to a token's `Pair` contract via a plain ERC20 `transfer`. The only functions capable of moving LT out of `Pair` are `Pair.transferAsset` (gated `onlyRouter`) reachable through `Router.sell` and `Router.graduate`, and both compute an amount that structurally excludes any donated LT. Once the curve pair is drained at graduation, or after the curve ends, the donated LT sits in `Pair` with no remaining code path to ever extract it.

### Finding Description
`Pair.transferAsset` is the sole withdrawal primitive for the asset (LT) side of a curve pair: [1](#0-0) 

It is `onlyRouter`, and `Router` exposes it through exactly two call sites:
- `Router.sell`, which computes `assetOut` from the curve's `k`-invariant math on the reserve state, not from `Pair`'s live balance: [2](#0-1) 
- `Router.graduate`, called only once from `Bonding._prepareGraduationLiquidity`, with an amount explicitly computed to exclude donations: [3](#0-2) [4](#0-3) 

The project's own documentation confirms the donated LT is left behind by design and calls the "lockedness" a mere trust assumption rather than an enforced guarantee: "Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`... 'Locked' here is a trust-assumption claim, not an on-chain guarantee." [5](#0-4) 

Unlike the token (base-currency) side, which is unconditionally burned when donated (`unsoldBurned` in `_prepareGraduationLiquidity`): [6](#0-5) 

there is no equivalent disposal or sweep for LT donated to `Pair`. Compare this to the two other places in the protocol where an accidental/donated balance can arrive: `FeeVault` has a permissionless `sweepDonations()` that forwards any USDC surplus above tracked balances to `feeTo`: [7](#0-6) 

and `Bonding` has `_sweepLTToOwner`, called at the end of every `finalizeGraduation`, to recover LT residue beyond a graduation's own earmark: [8](#0-7) 

`Pair.sol` has no analogous `skim`/`sweep`/rescue function at all — it only exposes `mint`, `swap`, `transferAsset`, `transferToken`, and view getters, all gated `onlyRouter`: [9](#0-8) 

Once a token's lifecycle flips past `Curve` (either `Graduated` after `finalizeGraduation`, or mid-`Graduating`), `Router.graduate` is never called again for that token — `Bonding` only calls it once, from `_prepareGraduationLiquidity`, which itself only runs from `_enterGraduating` (phase 1, invoked once per token). So any LT sent to `Pair` — before, during, or after the curve's life — that is not consumed by the exact `ltFromPair`/`sell` math is permanently stranded with zero remaining call path to move it anywhere.

### Impact Explanation
This is a permanent freezing of funds belonging to whoever sends LT to the pair address (mistaken transfer, or a deliberate "donation" attempt intending it to benefit the protocol/LP as the docs' own donation-resistance language implies is expected behavior for other flows). There is no owner, governance, or permissionless function anywhere in the codebase capable of moving LT out of a `Pair` except the two curve-internal, amount-capped paths described above. This matches a High-severity "unrecoverable funds sent to a contract with no recovery mechanism" bug class: value enters a contract that has an outflow gate (`onlyRouter`/curve math), but that gate can never be driven to release the donated portion, exactly mirroring the referenced report's `Timelock` fallback-ether scenario where `executeTransaction` could never be pointed at the stray ether.

### Likelihood Explanation
Reaching this requires nothing more than an unrelated wallet holding the paired LT and calling `IERC20(lt).transfer(pairAddress, amount)` — the `Pair` address is public (stored in `Bonding.tokenInfo[token].pair` and readable via `Factory`/events), and no allowlist or permission gates who may transfer ERC20 tokens into it. This can happen accidentally (a user mistakes the `Pair` for the `Zap`/`Bonding` entrypoint) or deliberately (an attacker intentionally donates dust or larger LT amounts, e.g. as a griefing vector against a creator/protocol expecting all raised LT to be recoverable, or simply loses funds by mistake). Given the multi-step buy/sell/graduate UX surface, at least accidental donations are plausible over the life of any given curve.

### Recommendation
Add a permissionless sweep/rescue function analogous to `FeeVault.sweepDonations()` / `Bonding._sweepLTToOwner()` for the `Pair` contract (or route through `Router`/`Bonding` with `BONDING_ROLE`), that computes `assetBalance() - assetReserve` (the portion of the LT balance beyond what the stored curve reserve accounts for) and forwards it to a designated recipient (e.g. the token's creator, the protocol `feeTo`, or burns it, consistent with how the token side already handles donations via unconditional burn). This should be callable both while `Lifecycle == Curve` and after graduation, so residue is never permanently unreachable regardless of when the donation lands relative to `_enterGraduating`/`finalizeGraduation`.

### Proof of Concept
1. `Bonding.launch(...)` a token; `Pair` is created and the curve trades normally.
2. Any unrelated wallet holding the paired LT calls `IERC20(lt).transfer(pairAddr, X)` directly (no interaction with `Zap`/`Bonding`/`Router` needed).
3. Curve trading (`Zap.buy`/`sell`) continues normally — `Router._computeBuy`/`_computeSell` and `Pair.swap`'s stored `_pool` reserves are untouched by the donation, since `Pair.swap` only mutates `_pool.tokenReserve`/`_pool.assetReserve` via explicit `tokenIn/tokenOut/assetIn/assetOut` arguments, never reading live `balanceOf`.
4. The token eventually graduates: `Bonding._prepareGraduationLiquidity` computes `ltFromPair = assetReserve - virtualLtReserve` from the *stored* reserve (excluding `X`) and calls `Router.graduate(token, ltFromPair)`, draining exactly that amount and leaving `X` behind in `Pair`.
5. `finalizeGraduation` completes; `info.lifecycle` becomes `Graduated`; `Router.graduate` will never be called again for this token.
6. `X` LT remains in `Pair` forever — no function in `Pair`, `Router`, `Bonding`, `Zap`, or any admin path can move it, since `Pair.transferAsset` is `onlyRouter` and `Router`'s only two callers of it (`sell`, one-shot `graduate`) never target this residual balance.

### Citations

**File:** packages/contracts/src/Pair.sol (L55-110)
```text
    function mint(
        uint256 tokenReserve,
        uint256 assetReserve
    ) external onlyRouter returns (bool) {
        if (_pool.k != 0) revert AlreadyMinted();
        _pool = Pool({tokenReserve: tokenReserve, assetReserve: assetReserve, k: tokenReserve * assetReserve});
        emit Mint(tokenReserve, assetReserve);
        return true;
    }

    function swap(
        uint256 tokenIn,
        uint256 tokenOut,
        uint256 assetIn,
        uint256 assetOut
    ) external onlyRouter returns (bool) {
        uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
        uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
        if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();

        _pool.tokenReserve = newTokenReserve;
        _pool.assetReserve = newAssetReserve;
        emit Swap(tokenIn, tokenOut, assetIn, assetOut);
        return true;
    }

    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }

    function transferToken(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(launchedToken).safeTransfer(recipient, amount);
    }

    function getReserves() external view returns (uint256, uint256) {
        return (_pool.tokenReserve, _pool.assetReserve);
    }

    function k() external view returns (uint256) {
        return _pool.k;
    }

    function tokenBalance() external view returns (uint256) {
        return IERC20(launchedToken).balanceOf(address(this));
    }

    function assetBalance() external view returns (uint256) {
        return IERC20(assetToken).balanceOf(address(this));
    }
}
```

**File:** packages/contracts/src/Router.sol (L165-182)
```text
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
```

**File:** packages/contracts/src/Router.sol (L184-211)
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

**File:** packages/contracts/src/Bonding.sol (L1079-1082)
```text
        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }
```

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }
```

**File:** docs/contracts-scope.md (L89-89)
```markdown
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
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
