## Finding: Catastrophic HyperSwap pre-seed can permanently brick `finalizeGraduation`, freezing the curve's raised LT and 250M reserve tokens

The CVE describes a high-privilege-but-network-reachable actor causing a **repeatable crash / permanent hang (DoS)** of a server via a legitimate-looking operation. The closest reachable analog in this codebase is an unprivileged attacker **permissionlessly pre-seeding the HyperSwap V2 TOKEN/LT pair** (explicitly listed as an in-scope reachable action) before graduation, in a way that makes `Bonding.finalizeGraduation` **deterministically and permanently revert** — a repeatable, un-recoverable "crash" of the one function that can move a token out of `Lifecycle.Graduating`.

### Root cause

`Bonding._routerDepositAndDispose` calls the HyperSwap V2 router's `addLiquidity` with `min0=1, min1=1` and never checks/handles a revert from the underlying `pair.mint()`: [1](#0-0) 

Standard UniswapV2 `mint()` semantics (mirrored by the project's own mock, `MockHyperswapPair.mint`) compute `liquidity = min(amount0 * totalSupply / reserve0, amount1 * totalSupply / reserve1)` for a non-empty pool and `require(liquidity > 0, ...)`: [2](#0-1) 

If an attacker inflates the pair's `totalSupply` far out of proportion to the eventual `(tokensForLP, ltFromPair)` deposit — a "catastrophic" hostile mint pre-seed — the balanced-subset deposit computed by `_pairRebalance`/`_routerDepositAndDispose` can still round `liquidity` to `0` inside the router's `addLiquidity → pair.mint` call, causing that call to **revert**, not to return `0`. Because `finalizeGraduation` performs no state changes until after `_seedUniswapV2Direct` returns, this revert unwinds the whole transaction, leaving `Lifecycle.Graduating` and `pendingGraduation[token]` byte-for-byte unchanged — so every subsequent call to `finalizeGraduation` re-derives the identical inputs and reverts identically: [3](#0-2) 

The project's own natspec acknowledges this exact edge is only partially defended: the 99%-budget cap on the rebalance swap is explicitly scoped as protecting the "realistic" pre-seed case, and calls out that "catastrophic pre-seeds beyond our budget capacity" are the case "where the alternative is bricking": [4](#0-3) 

Separately, even a legitimate `liquidity == 0` outcome from `_routerDepositAndDispose` (e.g. `remToken == 0` or `remLT == 0`) would still doom `finalizeGraduation`, because `LPLock.recordLock` hard-reverts on a zero amount and there is no retry/skip path: [5](#0-4) 

### Impact

Once a token enters `Lifecycle.Graduating`, trading is frozen and the curve's raised LT plus the 250M `LP_RESERVE` tokens sit in `Bonding` awaiting `finalizeGraduation`. There is no path back to `Lifecycle.Curve` and `LPLock` has no admin rescue in v1 (explicitly documented). If `finalizeGraduation` reverts deterministically for every caller, the token and its escrowed LT/tokens are **permanently frozen** — the on-chain equivalent of the CVE's "hang or frequently repeatable crash," except here it's not recoverable at all (no restart), which is strictly worse than the MySQL analog's availability impact.

### Likelihood

Requires an attacker to grow a HyperSwap V2 pool's `totalSupply` disproportionately to the eventual curve-close deposit size before phase 2 runs — capital-intensive but entirely permissionless (pair creation and `mint` are open to anyone), and the window between phase 1 (`_enterGraduating`) and phase 2 (`finalizeGraduation`) is attacker-observable on-chain.

### Recommendation

Wrap the `IUniswapV2Router02.addLiquidity` call in `_routerDepositAndDispose` (and the `pair.mint` in `_seedDirectMint`) in a `try/catch`, falling back to a router-independent direct-pair path (or skimming/burning the excess and recording a best-effort lock) so that no pre-seed shape — however extreme — can cause `finalizeGraduation` to revert unconditionally forever. Additionally, consider having `LPLock.recordLock` accept `amount == 0` as a no-op recorded lock rather than reverting, so a genuinely zero-liquidity graduation can still flip lifecycle to `Graduated` instead of being stuck.

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

**File:** packages/contracts/src/Bonding.sol (L1356-1378)
```text
    /// @dev Cap the rebalance swap at 99% of the available side's budget,
    ///      so the subsequent `addLiquidity` always has a non-zero amount
    ///      of BOTH sides to deposit. Without this, an extreme hostile
    ///      pre-seed (massively imbalanced reserves) drives the
    ///      unconstrained `_noFeeSwapInput` past our per-side budget,
    ///      `_pairRebalance` clamps to the full budget, and the swap
    ///      consumes 100% of one side. `_routerDepositAndDispose` then
    ///      skips `addLiquidity` (`remToken == 0` or `remLT == 0`),
    ///      `finalizeGraduation` returns `liquidity = 0`, and
    ///      `LPLock.recordLock(...)` records a zero-sized lock — the
    ///      attacker's pre-existing LP becomes 100% of the pool. Reserving
    ///      1% guarantees the deposit leg always lands AND mints non-zero
    ///      LP at the post-swap ratio. The 1% comes off the swap, not the
    ///      deposit — for any realistic pre-seed `s_unconstrained` is
    ///      orders of magnitude below `maxSwap`, so the cap doesn't bind
    ///      and behaviour is unchanged. It only kicks in for catastrophic
    ///      pre-seeds beyond our budget capacity, where the alternative
    ///      is bricking.
    function _swapBudget(
        uint256 budget
    ) internal pure returns (uint256) {
        return (budget * 99) / 100;
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

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L45-65)
```text
    function mint(
        address to
    ) external returns (uint256 liquidity) {
        uint112 reserve0 = _reserve0;
        uint112 reserve1 = _reserve1;

        uint256 balance0 = IERC20(token0).balanceOf(address(this));
        uint256 balance1 = IERC20(token1).balanceOf(address(this));
        uint256 amount0 = balance0 - reserve0;
        uint256 amount1 = balance1 - reserve1;

        uint256 totalSupply_ = totalSupply();
        if (totalSupply_ == 0) {
            liquidity = _sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY;
            _mint(DEAD, MINIMUM_LIQUIDITY);
        } else {
            uint256 liquidity0 = (amount0 * totalSupply_) / reserve0;
            uint256 liquidity1 = (amount1 * totalSupply_) / reserve1;
            liquidity = liquidity0 < liquidity1 ? liquidity0 : liquidity1;
        }
        require(liquidity > 0, "MockPair: INSUFFICIENT_LIQUIDITY_MINTED");
```

**File:** packages/contracts/src/LPLock.sol (L70-85)
```text
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
