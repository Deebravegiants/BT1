### Title
Unsized `transfer(pair, X) + sync()` pre-seed bypasses the hostile-pre-seed defense and seeds the graduated LP away from curve-close price - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._seedUniswapV2Direct` classifies any pre-seed of the not-yet-graduated HyperSwap V2 `(TOKEN, LT)` pair into three regimes keyed off `IUniswapV2Pair(pair).totalSupply()` and `skim()`-recoverable balance/reserve mismatches [1](#0-0) . The natspec explicitly acknowledges an attacker can leave the pair with `reserves > 0` and `totalSupply == 0` via `transfer(pair, dust) + sync()`, and asserts such "dust" is harmless because it "becomes reserves with no LP claim" [2](#0-1) . However, nothing bounds the size of that pre-synced reserve, and `_seedDirectMint` unconditionally transfers the cached `(tokensForLP, ltFromPair)` on top of whatever reserves are already sitting in the pair and then calls `pair.mint(lpLock)` [3](#0-2) . Because standard `UniswapV2Pair.mint` derives the pool's post-mint reserves (and thus its opening price) from `balance0`/`balance1` — not from the caller's transferred amounts alone — an attacker-sized (not dust-sized) `sync()`-based pre-seed on either side of the pair permanently skews the graduated LP's opening price away from the curve's closing price, even though the LP tokens themselves are minted 100% to `LPLock` with no claim for the attacker.

### Finding Description
The Regime-1/Regime-2 classification only guards against `pair.mint`-based pre-seeds (handled by rebalancing in Regime 3) and pure balance/reserve mismatches (handled by `skim()` in Regime 2). It does *not* guard against an attacker calling the permissionless, standard `IUniswapV2Pair.sync()` after donating tokens, which sets `reserve0`/`reserve1` equal to the live `balance0`/`balance1` [4](#0-3) . After such a call, `skim(address(this))` is a no-op (balance already equals reserves), `totalSupply() == 0` still holds, so `_seedUniswapV2Direct` routes to `_seedDirectMint`. That function does not read or account for the pair's pre-existing reserves at all — it simply adds `(tokensForLP, ltFromPair)` to whatever is already there and mints [5](#0-4) . Standard `UniswapV2Pair.mint`'s zero-supply branch computes `liquidity = sqrt(balance0 * balance1)` and sets `reserve0 = balance0, reserve1 = balance1` — i.e., the pool's *actual opening spot price* is `balance0/balance1`, which now includes the attacker's pre-seeded amount, not just the curve-close-derived `tokensForLP/ltFromPair`. Since `finalizeGraduation` is permissionless and callable by anyone once a token enters `Lifecycle.Graduating` (no minimum delay or freshness gate is enforced against phase 1) [6](#0-5) , any unrelated wallet can watch for the `TokenGraduating` event, front-run the keeper by pre-creating/pre-seeding the HyperSwap pair with an arbitrarily large one-sided donation plus `sync()`, and then let (or force) `finalizeGraduation` land on top of it.

### Impact Explanation
The graduated LP — which is immediately and irrevocably locked into `LPLock` via `recordLock` with no withdraw path [7](#0-6)  — opens at a price that deviates arbitrarily far from the curve's true closing price, in proportion to how large the attacker's donated side is relative to `tokensForLP`/`ltFromPair`. Because the attacker holds zero LP (all LP goes to `LPLock`), they cannot redeem the skewed pool directly, but any arbitrageur (including the attacker themselves via a separate swap) can trade the mispriced pool back toward the market/curve price, extracting value from the permanently-locked liquidity — a direct, unrecoverable loss to the protocol/LP position seeded at graduation, i.e. "an LP seeded away from the curve close price." This is exactly the documented invariant the surrounding natspec claims is preserved ("the pool opens at the exact curve-close price") [8](#0-7) , but the guarantee only holds for the size-limited `DIRECT_MINT_PRESEED_BPS` (1 bp) band inside `_seedRebalancing`'s Regime-3 path [9](#0-8)  — the top-level `totalSupply() == 0` fast path in `_seedUniswapV2Direct` has no equivalent size cap.

### Likelihood Explanation
`finalizeGraduation` is a fully permissionless function reachable by any unprivileged address the moment a token enters `Lifecycle.Graduating` [10](#0-9) . Pre-creating the HyperSwap V2 pair (`_ensureUniswapV2Pair` is idempotent and permissionless via the underlying factory) and donating tokens plus calling the pair's standard `sync()` requires no special privilege, no flash loan, and no race beyond front-running the keeper's ~60s finalize window, which any MEV-aware bot can win. The attack is cheap (bounded by the size of the donated tokens the attacker is willing to risk pre-seed capital on) and repeatable across every future graduation.

### Recommendation
Cap the size of pre-existing reserves accepted by the Regime-1 fast path (e.g., apply the same `DIRECT_MINT_PRESEED_BPS`-style bound used in `_seedRebalancing` to the `totalSupply() == 0` branch of `_seedUniswapV2Direct`, or unconditionally route to the rebalancing logic whenever `getReserves()` returns non-zero, regardless of `totalSupply()`), so that any non-negligible pre-existing reserve is arbed toward the cached curve-close ratio via `_pairRebalance` before minting, rather than being silently absorbed as-is by `_seedDirectMint`.

### Proof of Concept
1. Token `T` reaches `Lifecycle.Graduating`; `Bonding` caches `tokensForLP` / `ltFromPair` in `pendingGraduation[T]` at the curve-close ratio.
2. Before the keeper calls `finalizeGraduation`, an attacker calls `Factory(uniswapV2Factory).createPair(T, LT)` (or waits for `_ensureUniswapV2Pair` to do so), then `LT.transfer(pair, X)` for a large `X`, then `IUniswapV2Pair(pair).sync()`. This leaves `totalSupply() == 0`, `balance == reserve` (skim no-op), reserves = `(0, X)`.
3. Anyone calls `finalizeGraduation(T)`. `_seedUniswapV2Direct` sees `totalSupply() == 0` and calls `_seedDirectMint`, which transfers `tokensForLP` TOKEN and `ltFromPair` LT into the pair and calls `pair.mint(lpLock)`.
4. The pair's post-mint reserves are `(tokensForLP, ltFromPair + X)` — a price skewed from the curve-close ratio by the attacker-chosen `X`, with 100% of the (mispriced) LP locked in `LPLock`.
5. The attacker (or any arbitrageur) swaps against the pool to pull it back to fair value, extracting value from the locked LP position at the expense of the protocol/LP holders.

### Citations

**File:** packages/contracts/src/Bonding.sol (L955-980)
```text
    /// @notice Permissionless trigger for phase 1 of graduation. Same flow as
    ///         the inline post-buy trigger inside `_executeBuy`, but callable
    ///         without any buy. Closes the case where `canGraduate` is true
    ///         (LT appreciation pushed the curve past the USD threshold) but
    ///         the closing buy on the curve would mint below the BounceTech
    ///         LT mint floor and revert with `BelowMinTransactionSize`,
    ///         making the token un-graduatable via `Zap.buy`.
    /// @dev    `_enterGraduating` reads pair reserves and the launch-time
    ///         virtual reserve only — it does not depend on a buy having
    ///         just landed, so the same logic is safe to expose as a
    ///         standalone entry point. The lifecycle pre-checks mirror
    ///         `Bonding.buy`; the launch trading delay is intentionally
    ///         not enforced because `canGraduate` already requires either
    ///         the USD threshold or full curve sellout, both of which are
    ///         unreachable from a fresh launch within the delay window.
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

**File:** packages/contracts/src/Bonding.sol (L981-1002)
```text
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
```

**File:** packages/contracts/src/Bonding.sol (L1135-1142)
```text
    ///        1. **No LP minted yet — `totalSupply == 0` (~99% of
    ///           graduations).** A pristine empty pair, or a dust pre-seed
    ///           (`transfer(pair, dust) + sync()` leaves `reserves > 0` but
    ///           `totalSupply == 0`). Direct mint at exactly
    ///           `(tokensForLP, ltFromPair)` — V2's first-liquidity branch
    ///           makes those amounts the sole price input, so the pool opens
    ///           at the curve-close ratio and any dust becomes reserves with
    ///           no LP claim.
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

**File:** packages/contracts/src/Bonding.sol (L1245-1259)
```text
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
