### Title
Donation-inflated HyperSwap V2 pair reserves can force `finalizeGraduation` to compute zero LP liquidity, permanently reverting via `LPLock.recordLock`'s `ZeroAmount` check and freezing all curve-raised LT and the 250M LP-reserved tokens on `Bonding` forever - (`File: packages/contracts/src/Bonding.sol`)

### Summary
CVE-2019-0203 describes a remote, unprivileged actor sending a crafted protocol-command sequence that makes `svnserve` exit, permanently disrupting service for legitimate users. The alt.fun analog is a permissionless actor pre-creating and donation-inflating the HyperSwap V2 `(Token, LT)` pair before a token graduates, so that every future call to `Bonding.finalizeGraduation` computes a zero-liquidity LP mint. Because `LPLock.recordLock` hard-reverts on `amount == 0`, `finalizeGraduation` becomes permanently un-callable for that token, exactly mirroring the "certain sequence of commands crashes the process forever" pattern - except here the "process" is the graduation state machine, and the crash is a permanent, unrecoverable revert.

### Finding Description
`Bonding.finalizeGraduation` (`packages/contracts/src/Bonding.sol:1000-1034`) seeds the HyperSwap V2 LP via `_seedUniswapV2Direct` (`Bonding.sol:1201-1234`) and then unconditionally calls `LPLock(lpLock).recordLock(tokenAddress, lpPair, liquidity)` (`Bonding.sol:1031`).

`LPLock.recordLock` reverts with `ZeroAmount` whenever `amount == 0` (`packages/contracts/src/LPLock.sol:70-85`, specifically line 78). There is no way to skip or retry around this check, and `LPLock` explicitly has "No withdraw in v1" and an add-only locker set (`LPLock.sol:9,29-37`) - i.e., no on-chain recovery path exists once a token is stuck.

The hostile-pre-seed handling in `_seedUniswapV2Direct`/`_seedRebalancing`/`_seedDirectMint`/`_routerDepositAndDispose` (`Bonding.sol:1201-1486`) is carefully hardened against *pure, un-sync'd* donations (Regime 2, recovered via `pair.skim(address(this))` at `Bonding.sol:1215`) and against *swap-budget* edge cases (the 99% `_swapBudget` cap at `Bonding.sol:1356-1378`, explicitly documented to prevent a zero-liquidity mint). However, none of these defenses address the case where an attacker:

1. Pre-creates the `(Token, LT)` V2 pair (or lets `_ensureUniswapV2Pair` create it, then front-runs before phase 2).
2. Calls `pair.mint(attacker)` with the smallest possible amounts to obtain a tiny non-zero `totalSupply` (V2's `MINIMUM_LIQUIDITY` lock still allows `totalSupply` as low as ~1000).
3. `transfer`s a large amount of Token and/or LT directly to the pair and calls `sync()`, inflating `reserve0`/`reserve1` far beyond what `totalSupply` backs.

Because reserves are now synced (not merely a stray balance), `pair.skim(address(this))` at the top of `_seedUniswapV2Direct` pulls nothing - the donation is already counted in `getReserves()`. `_seedRebalancing`'s below-band check (`Bonding.sol:1297-1302`) and its swap-based rebalance (`_pairRebalance`, `Bonding.sol:1414-1429`) still route the deposit through either `_seedDirectMint` (a raw `pair.mint(lpLock)` call, `Bonding.sol:1245-1259`) or `_routerDepositAndDispose` (a `router.addLiquidity` call, `Bonding.sol:1449-1486`). Both ultimately invoke the *standard* Uniswap-V2 mint formula:

```
liquidity = min(amount0 * totalSupply / reserve0, amount1 * totalSupply / reserve1)
```

When `totalSupply` is deliberately kept minimal and one `reserve` side is pumped by the attacker's donation to be much larger than `amount * totalSupply`, that ratio integer-divides to `0`, so `liquidity = min(0, x) = 0` regardless of which seeding branch is taken (direct mint or router-mediated deposit). `finalizeGraduation` then calls `LPLock.recordLock(..., 0)`, which reverts every single time, for every retry, since the underlying pair state (tiny `totalSupply`, huge donated reserve) never changes and can only be made worse by further donations.

### Impact Explanation
Once a token is stuck in `Lifecycle.Graduating` with a permanently-reverting `finalizeGraduation`:
- The entire curve-raised LT reserve (`p.ltFromPair`, transferred into `Bonding` in `_prepareGraduationLiquidity` via `router.graduate`, `Bonding.sol:1084-1087`) is permanently locked in `Bonding` with no withdrawal path.
- The 250M tokens reserved for LP (`LP_RESERVE`, `Bonding.sol:67`, minus any burn) are permanently stranded in `Bonding`.
- The token can never reach `Lifecycle.Graduated`; no tradable AMM market is ever created, and all curve buyers/sellers who were counting on graduation lose access to a functioning secondary market.
- There is no owner/admin bypass: `LPLock`'s locker set is add-only and has no rescue function, and `Bonding.finalizeGraduation` has no alternate code path.

This is a permanent freeze of trader/creator funds (LT and LP-reserved tokens), satisfying the "concrete theft or permanent freezing of trader, creator or LP funds" bar.

### Likelihood Explanation
The attack is fully permissionless and requires only:
- The ability to create/interact with a standard HyperSwap V2 pair (`createPair`, `mint`, `transfer`, `sync` are all public/permissionless V2 pair operations), and
- Enough Token/LT balance to inflate one reserve side beyond the mint-formula's rounding threshold, which scales with the attacker-chosen (minimal) `totalSupply` they mint for themselves - i.e., the attacker controls both sides of the inequality and can tune `totalSupply` down to the V2 minimum to make the donation requirement as small as they like.

The window to execute this is any time before `Bonding.finalizeGraduation` first runs for a given token - i.e., between `launch()` and phase 2, or even opportunistically the instant a token enters `Lifecycle.Graduating` (phase 1) and before a keeper calls `finalizeGraduation`. Given `finalizeGraduation` is permissionless and keeper-driven with only a best-effort ~60s SLA (per the code's own natspec, `Bonding.sol:994-995`), an attacker monitoring `TokenGraduating` events has a race window, and can also pre-seed proactively for any token still in `Lifecycle.Curve` if they predict it will graduate.

### Recommendation
`_seedUniswapV2Direct`'s hostile-pre-seed defense needs to detect and neutralize the "minimal-`totalSupply`, inflated-`reserve`" case, not just the pure-donation (`skim`) and swap-rounds-to-zero cases already handled. Concrete options:
- After computing the intended `liquidity` (whether via the direct-mint or router-deposit path), check `liquidity > 0` before calling `LPLock.recordLock`; if it would be zero, fall back to a path that bypasses V2's ratio-based mint (e.g., burn/reset the hostile pool state by having `Bonding` become the majority LP holder through a proportionally scaled deposit, or add a minimum-deposit-to-reserve-ratio guard that forces a `_pairRebalance` large enough to raise `totalSupply`-backed liquidity above zero).
- Alternatively, detect a "reserve grossly exceeds totalSupply-backed value" condition explicitly (e.g., `reserve * MINIMUM_ACCEPTABLE_TOTALSUPPLY_RATIO`) and treat it the same as the Regime-2 donation case, sweeping/neutralizing the hostile reserve (e.g., via a compensating `skim`-equivalent achieved by first calling `sync()` back down, or minting into a fresh pair via `createPair` with a salt/nonce that the attacker cannot predict/front-run).
- Add an explicit non-zero-liquidity assertion inside `_seedUniswapV2Direct`/`finalizeGraduation` that reverts with a distinct, retryable error rather than silently reaching `LPLock.recordLock(0)` - and pair that with an owner-gated emergency recovery function on `LPLock`/`Bonding` for tokens stuck in `Lifecycle.Graduating` beyond a timeout, so a governance-mediated rescue is possible even if the AMM-level fix is imperfect.

### Proof of Concept
Conceptual sequence (all steps callable by a single unprivileged EOA):
1. Wait for/observe a token `T` approaching graduation (`Bonding.canGraduate(T)` about to flip true), with LT reserve `ltFromPair` and `tokensForLP` known/estimable from `previewLtUntilGraduation` and pair reserves.
2. Call `IUniswapV2Factory.createPair(T, LT)` to create the pair before `Bonding` does (or race the phase-1→phase-2 window if the pair already exists empty).
3. Acquire a small amount of `T` (e.g., via a curve buy) and LT, and call `pair.mint(attacker)` with minimal amounts so `pair.totalSupply()` is just above `MINIMUM_LIQUIDITY` (e.g., `~1000`).
4. `transfer` a large amount of LT (or `T`) directly to the pair and call `pair.sync()`, inflating `reserveLT` (or `reserveToken`) far above `amount * totalSupply` for the eventual `tokensForLP`/`ltFromPair` that `Bonding` will deposit.
5. Trigger/await the token's graduation (`Bonding.triggerGraduation` or the inline buy trigger) and call `Bonding.finalizeGraduation(T)`.
6. `_seedUniswapV2Direct` takes the Regime-3 rebalance path; `skim` recovers nothing (reserves already synced); either `_seedDirectMint` or `_routerDepositAndDispose` computes `liquidity = min(amount0*totalSupply/reserve0, amount1*totalSupply/reserve1) == 0` due to the inflated reserve; `LPLock.recordLock(T, lpPair, 0)` reverts with `ZeroAmount`; the entire `finalizeGraduation` transaction reverts.
7. Every subsequent call to `finalizeGraduation(T)` reverts identically - the token, its curve-raised LT, and its 250M LP-reserved tokens are permanently stuck with `Lifecycle.Graduating`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1201-1259)
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

**File:** packages/contracts/src/Bonding.sol (L1279-1354)
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
        } else if (reserveToken * ltFromPair < reserveLT * tokensForLP) {
            // Pool LT-rich. tokenIn = tokenAddress, tokenInIs0 = tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: tokenAddress,
                        tokenInIs0: tokenIs0,
                        reserveIn: reserveToken,
                        reserveOut: reserveLT,
                        targetN: tokensForLP,
                        targetD: ltFromPair,
                        maxSwap: _swapBudget(IERC20(tokenAddress).balanceOf(address(this)))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        }
        // else: pool already at curve-close ratio (rare — e.g. attacker
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1449-1486)
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

        // Burn off-ratio TOKEN remainder (`Bonding` is the Token owner).
        // Hostile pre-seeds reduce circulating supply by the attacker's
        // wasted-side share, net positive for honest holders.
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
        // LT remainder is third-party — we cannot burn it. It stays in
        // this contract until `finalizeGraduation`'s post-bookend sweeps
        // it to the owner. Honest graduations never reach this code path,
        // so the residue is zero outside attack scenarios.
    }
```

**File:** packages/contracts/src/LPLock.sol (L9-37)
```text
/// @notice Locks LP tokens from graduated tokens. No withdraw in v1.
/// @dev UUPS-upgradeable to support v2 `migrateLT` functionality.
///      Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
///
///      Storage uses ERC-7201 namespaced layout (no `__gap` needed). All
///      mutable state lives in `LPLockStorage` at `_LP_LOCK_STORAGE_LOCATION`.
contract LPLock is UUPSUpgradeable, Ownable2StepUpgradeable {
    struct LockInfo {
        address lpPair;
        uint256 amount;
        uint256 lockedAt;
    }

    /// @custom:storage-location erc7201:altfun.storage.LPLock
    struct LPLockStorage {
        mapping(address token => LockInfo) locks;
        /// @dev Locker allowlist for `recordLock`. Add-only via `addLocker` —
        ///      there is no removal path. A live revoke would brick every
        ///      in-flight `Bonding.finalizeGraduation` (token permanently
        ///      stuck in `Lifecycle.Graduating`, no on-chain recovery), so
        ///      the only way to retire a locker is a UUPS upgrade — which
        ///      surfaces on-chain ahead of time instead of as a one-tx kill
        ///      switch.
        mapping(address account => bool) isLocker;
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
