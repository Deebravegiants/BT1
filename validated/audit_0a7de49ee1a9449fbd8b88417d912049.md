### Title
Direct LT transfers into a curve `Pair` are permanently and irrecoverably locked, with no rescue path pre- or post-graduation - (File: `packages/contracts/src/Pair.sol`)

### Summary
`Pair.sol` holds the reserve LT (leveraged token) for a bonding curve, but the only function capable of moving `assetToken` out of the contract, `transferAsset`, is gated `onlyRouter` and is invoked from exactly two call sites in the whole system: `Router.sell` (only reachable while the token's lifecycle is `Curve`) and `Router.graduate` (called exactly once, from `Bonding._prepareGraduationLiquidity`, and permanently unreachable for a given token once its lifecycle passes `Curve`). Any LT sent directly to a `Pair` address outside of these accounted flows — most importantly, any LT donated to the pair after the token has entered `Graduating`/`Graduated` — has no code path anywhere in the protocol that can ever move it out again. This mirrors the external report's bug class exactly: an asset-holding contract with no withdrawal function for a token it can receive, resulting in permanent loss of funds.

### Finding Description
`Pair.transferAsset` is the sole function that transfers the reserve asset (`assetToken`, the LT) out of a `Pair`: [1](#0-0) 

It is `onlyRouter`, and `Router.sol` exposes it through only two paths: `Router.sell` (curve trading) and `Router.graduate` (graduation drain): [2](#0-1) 

`Router.graduate` is called from exactly one place in `Bonding.sol`, `_prepareGraduationLiquidity`, which drains `ltFromPair = assetReserve - virtualLtReserve` — deliberately excluding any LT that was donated directly to the pair (donations don't move the *stored* `assetReserve`): [3](#0-2) 

`_prepareGraduationLiquidity` itself only ever runs once per token, from `_enterGraduating`, which is gated to run only while `Lifecycle == Curve` (via `Bonding.buy`'s inline trigger or `triggerGraduation`'s explicit `if (info.lifecycle != Lifecycle.Curve) revert`): [4](#0-3) 

The protocol's own documentation acknowledges this is a one-way trust boundary: donated LT "remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`" and that "`Bonding` in turn only calls `graduate` from `_prepareGraduationLiquidity` — which is unreachable once the token's lifecycle has flipped past `Curve`. So the leftover is unreachable..." [5](#0-4) 

There is no admin sweep, no owner rescue, and no alternate withdrawal function on `Pair.sol` — the contract exposes only `mint`, `swap`, `transferAsset`, `transferToken`, and view functions: [6](#0-5) 

Consequently: (1) any LT donated to a `Pair` while the token is still on the `Curve` lifecycle is excluded from the graduation drain by design and stays locked forever once graduation fires (a one-time, single-call drain that can never be repeated for that token); (2) any LT sent to the `Pair` address at any time *after* the token has entered `Graduating` or `Graduated` is unconditionally and permanently stuck, since `Router.graduate` for that token is now forever unreachable and `Router.sell` is blocked once trading is frozen. In both cases the LT is real, valuable, third-party-owned economic value that cannot be burned (unlike donated launched-`Token`, which `_prepareGraduationLiquidity`/`_routerDepositAndDispose` explicitly burn) and cannot be transferred out by any function in the codebase.

### Impact Explanation
This is a permanent freeze of funds inside a core in-scope contract (`Pair`), matching the "permanent freezing of trader, creator or LP funds" criterion. LT is a yield-bearing, real-value asset (BounceTech leveraged token); once trapped it is unrecoverable by the protocol owner, the original sender, or any other party — there is no governance/admin sweep analogous to `FeeVault.sweepDonations()` or `Bonding._sweepLTToOwner` covering this contract. Any mistaken direct transfer (a common user error pattern — sending assets straight to a pool/pair address instead of through the intended `Zap`/`Bonding` entry points) or any LT that lands in the pair post-graduation is lost forever. Given the protocol handles real leveraged-token value across every launched token's curve pair, the surface for this loss is present on every single `Pair` deployed by the `Factory`.

### Likelihood Explanation
Likelihood is Medium: it requires an unrelated wallet or the token creator/trader to send LT directly to a `Pair` address (via `IERC20.transfer`) rather than through `Zap`, which can happen accidentally (fat-fingered transfers, bots copying the wrong contract address, or third-party integrations that don't understand the curve/graduated split) or as accepted "donation" behavior the docs already anticipate. No privileged role or attacker cooperation is needed — a single unprivileged `IERC20(lt).transfer(pairAddr, amount)` call is sufficient, and the loss is deterministic and total for any transfer that lands after the token has left `Lifecycle.Curve`.

### Recommendation
- Short term: Add an owner- or governance-gated sweep function on `Pair.sol` (or a `Router`-mediated rescue callable by `Bonding`'s owner) that can transfer out any `assetToken`/`launchedToken` balance held by the `Pair` beyond its accounted `_pool` reserves, similar in spirit to `FeeVault.sweepDonations()` and `Bonding._sweepLTToOwner`, but reachable at any lifecycle stage (including post-`Graduated`).
- Long term: Add invariant/regression tests (mirroring `GraduationInvariants.t.sol`'s donation tests) that specifically assert donated/stray LT sent to a `Pair` post-graduation can be recovered by a defined rescue path, and document the full fund-flow lifecycle for `Pair`-held assets across `Curve` → `Graduating` → `Graduated` states.

### Proof of Concept
1. A token launches via `Bonding.launch`/`Zap.createToken`, creating `Pair` P for `(Token T, LT L)`.
2. The token trades normally on the curve and eventually graduates: `_enterGraduating` fires, `_prepareGraduationLiquidity` drains `ltFromPair` via `Router.graduate`, and `finalizeGraduation` flips `info.lifecycle` to `Lifecycle.Graduated` (`packages/contracts/src/Bonding.sol` lines 1000-1034).
3. Any wallet now calls `IERC20(L).transfer(pairAddress, X)`, sending LT directly into `Pair` P.
4. `Pair.assetBalance()` now includes `X`, but no function anywhere in the protocol can extract it: `Router.graduate` is `onlyRole(BONDING_ROLE)` and only invoked once per token from `_prepareGraduationLiquidity`, which is unreachable for a token already `Graduated`; `Router.sell` requires the token to still be trading on the curve, which it no longer is.
5. `X` LT is permanently locked in `Pair` P with no owner, creator, or protocol-level recovery mechanism.

### Citations

**File:** packages/contracts/src/Pair.sol (L55-109)
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
```

**File:** packages/contracts/src/Router.sol (L184-202)
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
```

**File:** packages/contracts/src/Router.sol (L203-211)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }
```
