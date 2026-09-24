### Title
LP graduation seeding trusts an unbounded "dust" pre-seed on the empty-supply branch, letting an attacker skew the graduated pool off the curve-close price - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._seedUniswapV2Direct` branches on `IUniswapV2Pair(pair).totalSupply() == 0` to decide whether the HyperSwap V2 pair is "pristine" and safe to seed directly at the cached curve-close ratio via `_seedDirectMint`. This branch assumes any pre-existing reserves on a zero-supply pair are negligible "dust" from `transfer + sync()`. Unlike the sibling non-zero-supply branch (`_seedRebalancing`), which explicitly caps how much pre-seed it will tolerate before switching from a rebalance to a direct mint (`DIRECT_MINT_PRESEED_BPS`), the zero-supply branch has **no size check at all** — it unconditionally calls `_seedDirectMint` regardless of how large the pre-seeded reserves are, as long as `mint()` was never called on the pair. [1](#0-0) 

### Finding Description
`_seedUniswapV2Direct` first `skim()`s the pair, then checks:
```solidity
if (IUniswapV2Pair(pair).totalSupply() == 0) {
    return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
}
``` [1](#0-0) 

`skim()` only forwards `balance - reserve` to `Bonding`; if an attacker calls the pair's standard `sync()` after donating tokens (as the code's own natspec acknowledges: "a dust pre-seed from `transfer(pair, dust) + sync()` that leaves reserves non-zero while supply is still zero"), then `balance == reserve` and `skim()` is a no-op — the donation is *not* pulled out. [2](#0-1) 

`_seedDirectMint` then transfers the cached `tokensForLP`/`ltFromPair` on top of the existing (attacker-controlled) reserves and calls `pair.mint(lpLock)`:
```solidity
IERC20(tokenAddress).safeTransfer(pair, tokensForLP);
IERC20(lt).safeTransfer(pair, ltFromPair);
liquidity = IUniswapV2Pair(pair).mint(_s().lpLock);
``` [3](#0-2) 

In standard UniswapV2 semantics (the exact model this codebase targets, per `IUniswapV2Pair`), when `totalSupply == 0`, `mint()` computes `liquidity = sqrt(amount0 * amount1)` where `amount0`/`amount1` are the *diffs* from the already-synced reserves — so the LP-share calculation correctly excludes the pre-existing dust (matching the comment "any dust becomes reserves with no LP claim"). However, the pair's **new reserves are set to the full post-transfer balances** (dust + `tokensForLP`/`ltFromPair`), which become the pool's live spot price. If the attacker's donated "dust" is not actually small, the resulting price is `(dust_token + tokensForLP) / (dust_lt + ltFromPair)`, which diverges arbitrarily from the intended curve-close ratio `tokensForLP / ltFromPair` that the rest of the graduation machinery (`_prepareGraduationLiquidity`, `_launchTimeVirtualLtReserve`) is carefully designed to preserve.

This is directly analogous to the reported CVE's root cause: a security-relevant classification (`totalSupply()==0` ⇒ "safe, empty/negligible-dust pair") is applied uniformly to two *semantically different* pre-seed mechanisms — the checked/bounded one (mint-based pre-seed, `totalSupply()>0`, guarded by `DIRECT_MINT_PRESEED_BPS`) and an unchecked one (`transfer`+`sync()`-based pre-seed, `totalSupply()==0`, with no size guard) — exactly as `gethostbyname()` was trusted to classify all hostnames while silently missing the AAAA/IPv6 resolution path.

### Impact Explanation
An attacker can, before the target token graduates:
1. Call the permissionless `IUniswapV2Factory.createPair(tokenAddress, lt)` on HyperSwap V2 to pre-create the exact pair `Bonding._ensureUniswapV2Pair` will later reuse. [4](#0-3) [5](#0-4) 
2. Buy curve tokens via `Zap.buy`/`Bonding.buy` and acquire LT on the open market, then `transfer` large amounts of both directly into the pre-created pair and call `sync()` — all standard, permissionless V2 pair operations. [6](#0-5) 
3. Trigger or wait for graduation (`triggerGraduation` is permissionless) and call `finalizeGraduation`, also permissionless. [7](#0-6) [8](#0-7) 

The graduated LP is then permanently locked at a price skewed by the attacker's chosen dust ratio — the exact "LP seeded away from the curve close price" impact this exercise is scoped to accept. The mispricing enables the attacker (or any third party) to immediately arbitrage the freshly graduated, `LPLock`-locked pool against the true curve-close price, extracting value from the LP/creator/traders, with no rescue path since `LPLock` has no withdrawal mechanism per the code's own documentation. [9](#0-8) 

### Likelihood Explanation
Every primitive required — `createPair`, ERC20 `transfer`, `sync()`, curve `buy`, `triggerGraduation`, `finalizeGraduation` — is callable by any unprivileged address, and the rules of engagement explicitly flag "pre-creating or pre-seeding the HyperSwap V2 TOKEN/LT pair before graduation" as in-scope. The attacker only needs enough capital to acquire the token/LT amounts they wish to donate as "dust" (their cost is bounded by what they can then arbitrage back, plus whatever they choose to skew the price by, since none of it becomes their own LP share). No special timing or race condition beyond acting before `finalizeGraduation` is required — a straightforward, front-runnable sequence.

### Recommendation
Apply the same smallness bound used in the non-zero-supply branch to the zero-supply branch: before treating `totalSupply()==0` as "safe empty/negligible pair," check the pair's live reserves against `tokensForLP`/`ltFromPair` using the same `DIRECT_MINT_PRESEED_BPS` threshold (or reject/rebalance instead of direct-minting) whenever non-zero reserves exist. Alternatively, unify both regimes so any non-zero pre-existing reserve — whether created via `mint` or via `transfer+sync` — always goes through the `_seedRebalancing` size check rather than being fast-pathed by the `totalSupply()==0` test alone.

### Proof of Concept
1. Attacker calls `IUniswapV2Factory(uniswapV2Factory).createPair(tokenAddress, ltAddress)` for a token that has not yet graduated.
2. Attacker buys curve tokens via `Zap`/`Bonding.buy` and separately acquires LT, then `transfer`s a large, deliberately skewed amount of both into the newly created pair (e.g., mostly `tokenAddress`, minimal `lt`), then calls `IUniswapV2Pair(pair).sync()`. `totalSupply()` remains `0` since `mint()` was never called.
3. Attacker (or anyone) drives/awaits `canGraduate(tokenAddress)` to true and calls `Bonding.triggerGraduation(tokenAddress)`, then `Bonding.finalizeGraduation(tokenAddress)`.
4. Inside `finalizeGraduation` → `_seedUniswapV2Direct`: `skim()` is a no-op (`balance == reserve` post-sync); `totalSupply() == 0` is true, so `_seedDirectMint` transfers `tokensForLP`/`ltFromPair` on top of the attacker's dust and calls `pair.mint(lpLock)`.
5. The resulting locked pool reserves are `(dust_token + tokensForLP, dust_lt + ltFromPair)` — priced far from `tokensForLP / ltFromPair` (the true curve-close price) whenever the attacker's dust is large relative to `tokensForLP`/`ltFromPair`, and this mispriced, locked pool cannot be corrected afterward.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1121-1130)
```text
    function _ensureUniswapV2Pair(
        address tokenA,
        address tokenB
    ) internal returns (address pair) {
        IUniswapV2Factory v2Factory = IUniswapV2Factory(_s().uniswapV2Factory);
        pair = v2Factory.getPair(tokenA, tokenB);
        if (pair == address(0)) {
            pair = v2Factory.createPair(tokenA, tokenB);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1148-1154)
```text
    ///           handled by `finalizeGraduation`'s post-bookend
    ///           `_sweepLTToOwner` (which uses `protectedLT` snapshotted
    ///           BEFORE skim, so the donation is correctly classified as
    ///           rebalance residue rather than concurrent-graduation
    ///           escrow). NEVER routed to `LPLock` — `LPLock` has no
    ///           rescue path in v1, so anything that lands there is
    ///           permanently stuck.
```

**File:** packages/contracts/src/Bonding.sol (L1209-1226)
```text
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

**File:** packages/contracts/src/interfaces/IUniswapV2Factory.sol (L7-16)
```text
interface IUniswapV2Factory {
    function getPair(
        address tokenA,
        address tokenB
    ) external view returns (address pair);
    function createPair(
        address tokenA,
        address tokenB
    ) external returns (address pair);
}
```

**File:** packages/contracts/src/interfaces/IUniswapV2Pair.sol (L37-45)
```text
    /// @notice Force the pair to send any token balance in excess of stored
    ///         `reserve0/reserve1` to `to`. Used by `Bonding.finalizeGraduation`
    ///         to sweep pure-donation pre-seeds (raw `transfer` to the pair
    ///         without `mint`) before the rebalance, so donated tokens don't
    ///         pollute the post-swap ratio computation. Pure-mint pre-seeds
    ///         leave `balance == reserves` and are unaffected.
    function skim(
        address to
    ) external;
```
