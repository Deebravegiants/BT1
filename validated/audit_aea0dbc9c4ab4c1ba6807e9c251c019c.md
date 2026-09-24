## Fee-bypass analog: Bonding.buy/sell can be called directly, skipping Zap's fee layer entirely

### Title
Trading directly against `Bonding.buy`/`Bonding.sell` bypasses all protocol and creator fees - (File: `packages/contracts/src/Router.sol`, `packages/contracts/src/Zap.sol`)

### Summary
The reported bug is that IndexPool's swap path has no fee-collection call at all — fees only exist in a sibling pool type, so an LP/trader path silently earns zero protocol fees, undermining the fee model and pushing liquidity toward the un-fee'd pool. alt.fun has the analogous architectural split: the AMM engine itself (`Router`/`Bonding`) charges **no fee whatsoever**, and the entire 0.75% buy/sell fee is only levied by the `Zap` wrapper that calls into `Bonding` on the user's behalf.

### Finding Description
`Router.sol` explicitly documents that it holds no fee logic: *"No fees here — `Zap` handles fees."* [1](#0-0) . `Router.buy`/`Router.sell` are gated only by `BONDING_ROLE`, i.e. callable by `Bonding` [2](#0-1) [3](#0-2) .

Fees are assessed only inside `Zap._buyInternal`/`_sellInternal`, which mint/redeem LT and then call `bonding_.buy(...)`/`bonding_.sell(...)` before or after computing and forwarding the fee to `FeeVault` via `_accrueFee` [4](#0-3) [5](#0-4) . The docs confirm the entire fee model — "All fees are charged by `Zap` in USDC and forwarded into `FeeVault`. The router holds no fee state" [6](#0-5) .

`Bonding.buy`/`Bonding.sell` accept an explicit `to`/trader argument (see the call signature `bonding_.buy(ltAmount, tokenAddress, 0, msg.sender)` used by `Zap`) [7](#0-6) . I was not able to fully confirm, within the remaining tool budget, whether `Bonding.buy`/`Bonding.sell` are restricted to `msg.sender == address(Zap)` (e.g. a `ZAP_ROLE`/`onlyZap` modifier) or are open `external`/`public` entry points that any address holding the underlying LT (or curve tokens, for sell) can call directly. My greps for `onlyRole`/`ZAP_ROLE`/`onlyZap` inside `Bonding.sol` returned matches but I could not read the surrounding function bodies before running out of iterations, so **this cannot be treated as conclusively proven** — it needs direct inspection of `Bonding.sol`'s `buy`/`sell` function modifiers.

### Impact Explanation
If `Bonding.buy`/`Bonding.sell` are indeed unrestricted (callable by any EOA that already holds LT, which is obtainable permissionlessly by minting directly against BounceTech, outside of `Zap`), then a trader can execute the entire curve trade — mint via BounceTech directly, then call `Bonding.buy(ltAmount, token, minOut, self)` — and receive curve tokens with **zero fee deducted**, since `Router`/`Bonding` charge nothing and `FeeVault.accrue` is only ever invoked from `Zap._accrueFee`. This permanently starves `FeeVault` of both the 0.5% protocol share and the 0.25% creator share on every such trade, exactly mirroring the IndexPool report's root cause (an AMM engine with a working fee mechanism next to it that the swap path never invokes).

### Likelihood Explanation
Depends entirely on whether `Bonding.buy`/`sell` enforce a caller restriction. If they don't, likelihood is high — any sophisticated trader/bot would trivially route around `Zap` to avoid the 0.75% fee, since `Bonding.buy` requires only LT (mintable directly from BounceTech with USDC) rather than a `Zap`-specific call.

### Recommendation
Confirm in `packages/contracts/src/Bonding.sol` whether `buy`/`sell` are gated to `msg.sender == zap` (or equivalent role). If not, either (a) add such a restriction so all trades must route through `Zap`'s fee layer, or (b) move fee assessment into `Router`/`Bonding` itself so it can't be bypassed regardless of caller.

### Proof of Concept
Cannot be finalized without confirming `Bonding.sol`'s access control on `buy`/`sell`. This requires a Devin session with full file access to `packages/contracts/src/Bonding.sol` to inspect the exact modifiers on `buy`/`sell` and, if unrestricted, to write a Foundry PoC that: (1) mints LT directly from BounceTech with USDC, (2) calls `Bonding.buy` directly (bypassing `Zap`), and (3) asserts `FeeVault`'s balance and `FeeAccrued` event are unchanged, versus the equivalent trade through `Zap.buy` which does accrue fees.

### Citations

**File:** packages/contracts/src/Router.sol (L11-18)
```text
/// @title Router
/// @notice AMM math for bonding-curve pairs. No fees here — `Zap` handles fees.
/// @dev Supports virtual token reserves (curve extends beyond sellable supply,
///      enabling zero-gap LP seeding at graduation).
///
///      No reentrancy guard: all entry points are gated by `BONDING_ROLE`, and
///      `Bonding` wraps every trade in `nonReentrant`. Granting `BONDING_ROLE`
///      to any caller that doesn't enforce non-reentrancy would be unsafe.
```

**File:** packages/contracts/src/Router.sol (L92-108)
```text
    function buy(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);

        (amountInUsed, tokensOut) = _computeBuy(pairAddr, amountIn);

        IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);

        IPair(pairAddr).transferToken(to, tokensOut);
        IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
    }
```

**File:** packages/contracts/src/Router.sol (L150-170)
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
```

**File:** packages/contracts/src/Zap.sol (L454-469)
```text
        // Symmetric with `_executeBuy`: fee charged on EVERY sell — curve
        // AND post-graduation. The `isGraduated` branch above selects the
        // venue, not the fee policy. See `_executeBuy` for the rationale.
        uint256 fee = Math.mulDiv(grossUsdc, $.sellFeeBps, BPS_DENOM, Math.Rounding.Ceil);
        usdcOut = grossUsdc - fee;

        if (usdcOut < minUsdcOut) revert SlippageExceeded();

        $.usdc.safeTransfer(msg.sender, usdcOut);

        if (fee > 0) {
            _accrueFee(tokenAddress, bonding_.creatorOf(tokenAddress), fee, false);
        }

        emit Sell(tokenAddress, msg.sender, tokenAmount, usdcOut);
    }
```

**File:** packages/contracts/src/Zap.sol (L507-530)
```text
    function _buyOnCurve(
        address tokenAddress,
        address lt,
        uint256 ltAmount
    ) internal returns (uint256 tokensOut, uint256 amountInUsed) {
        Bonding bonding_ = _s().bonding;
        Router curveRouter = bonding_.router();
        IERC20(lt).forceApprove(address(curveRouter), ltAmount);
        // Slippage check happens after the refund path in `_buyInternal`.
        // `msg.sender` here is the user-EOA that called `Zap.buy`; passed
        // through as `trader` for the emitted `Trade` event.
        (tokensOut, amountInUsed) = bonding_.buy(ltAmount, tokenAddress, 0, msg.sender);
        IERC20(lt).forceApprove(address(curveRouter), 0);
    }

    function _sellOnCurve(
        address tokenAddress,
        uint256 tokenAmount
    ) internal returns (uint256 ltReceived) {
        Bonding bonding_ = _s().bonding;
        Router curveRouter = bonding_.router();
        IERC20(tokenAddress).forceApprove(address(curveRouter), tokenAmount);
        ltReceived = bonding_.sell(tokenAmount, tokenAddress, 0, msg.sender);
    }
```

**File:** docs/contracts-scope.md (L112-120)
```markdown
## Fees & FeeVault

All fees are charged by `Zap` in USDC and forwarded into `FeeVault`. The router holds no fee state — the vault is where balances live and where creators and the protocol claim.

- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
```
