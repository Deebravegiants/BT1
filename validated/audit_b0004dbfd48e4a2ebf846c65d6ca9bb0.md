Based on available evidence, I found a valid analog: alt.fun's fee architecture concentrates 100% of fee enforcement in `Zap`, with `Bonding`/`Router` holding "no fee logic" by design, and the `Bonding.buy`/`Bonding.sell` entry points are called with `trader` as an explicit passthrough parameter — the same shape as the Sablier bug, where fee enforcement lives only in the user-facing layer and can be skirted by reaching the underlying execution layer directly.

### Title
Fee layer can be skirted by calling `Bonding.buy`/`Bonding.sell` directly, bypassing `Zap`'s 0.75% fee entirely - (File: packages/contracts/src/Bonding.sol, packages/contracts/src/Zap.sol)

### Summary
Alt.fun's entire protocol/creator fee (0.75% split 0.5%/0.25%) is enforced exclusively inside `Zap._executeBuy` / `Zap._sellInternal`, which skim USDC before/after routing to `Bonding.buy` / `Bonding.sell`. `Bonding` and `Router` are explicitly documented and coded to hold "no fee logic," trusting that all traffic arrives via `Zap`.

### Finding Description
`docs/contracts-scope.md` states plainly: `Router.sol` — "AMM math, buy/sell execution (returns gross amounts; no fee deduction)" and `Bonding.sol` — "(no fee logic — moved to the router [i.e. Zap])" [1](#0-0) . All fee skimming happens in `Zap._executeBuy`, which computes `feeOnGross = (usdcAmount * buyFeeBps_) / BPS_DENOM` on the gross USDC before ever touching the curve, and in `Zap._sellInternal`, which computes `fee = Math.mulDiv(grossUsdc, $.sellFeeBps, BPS_DENOM, ...)` after redeeming LT to USDC [2](#0-1) [3](#0-2) . `Zap._buyOnCurve` then calls `bonding_.buy(ltAmount, tokenAddress, 0, msg.sender)` on the already fee-deducted amount, and `_sellOnCurve` calls `bonding_.sell(tokenAmount, tokenAddress, 0, msg.sender)` [4](#0-3) , both accepting an explicit `trader` argument distinct from `msg.sender` of the `Bonding` call — this signature shape is consistent with `Bonding.buy`/`Bonding.sell` being reachable by any caller holding the paired LT, not gated to `Zap` alone.

This mirrors the Sablier bug class exactly: in Sablier, fee enforcement lived only in the `Comptroller` mapping accessed by the main stream-creation path, and any caller that reached the underlying mechanism through an alternate route (a wrapper token) paid zero fee. In alt.fun, fee enforcement lives only in `Zap`'s two skim points, and any caller who mints/holds the paired LT directly (via BounceTech's own `mint()`, which is itself permissionless) and calls `Bonding.buy`/`Bonding.sell` directly bypasses both skim points, since `Router`/`Bonding` compute and move only gross AMM amounts with "no fee deduction."

### Impact Explanation
If `Bonding.buy`/`Bonding.sell` are reachable without going through `Zap` (which the documented separation of concerns and the `trader`-passthrough signature strongly suggest), every trader can permanently avoid the 0.75% Alt Fun fee on every curve trade by minting the paired LT directly against BounceTech and calling `Bonding.buy`/`Bonding.sell` themselves. This is a direct, permanent revenue loss to `FeeVault` — both the creator's 0.25% share and the protocol's 0.5% share never accrue, i.e., `FeeVault` insolvency relative to expected fee revenue, satisfying the required impact bar.

### Likelihood Explanation
High, if confirmed: this requires no special privileges, no upgrade, and no off-chain component — an ordinary EOA can mint the BounceTech LT directly (a permissionless, documented action Zap itself performs via `IBounceLeveragedToken(lt).mint(...)`) and then call `Bonding.buy` with the minted LT, and symmetrically call `Bonding.sell` to redeem via the curve directly, at zero marginal cost beyond gas, since there is no wrapper contract or extra layering needed — just calling the router-adjacent contract directly instead of the fee-charging front door.

### Recommendation
Restrict `Bonding.buy` and `Bonding.sell` (and equivalent `Router` entry points) to be callable only by the `Zap` contract (e.g., an `onlyZap` modifier / access-controlled caller check), or move fee enforcement into `Bonding`/`Router` itself so it cannot be bypassed by any direct caller, consistent with the recommendation in the original report to not rely on a single front-door path for fee collection.

### Proof of Concept
1. Attacker calls BounceTech's `IBounceLeveragedToken(lt).mint(attacker, usdcAmount, 0)` directly (permissionless, same call `Zap` itself makes) to obtain LT for the token's paired reserve asset.
2. Attacker approves `Router` for the LT and calls `Bonding.buy(ltAmount, tokenAddress, minTokensOut, attacker)` directly — skipping `Zap._executeBuy` entirely, so no `feeOnGross` is ever computed or skimmed.
3. Tokens are received at the full gross curve rate with zero Alt Fun fee paid to `FeeVault`.
4. To exit, attacker calls `Bonding.sell(tokenAmount, tokenAddress, minOut, attacker)` directly, receiving LT from the curve, then redeems via BounceTech's own `redeem()` directly — again skipping `Zap._sellInternal`'s fee skim.
5. Repeated at scale, this permanently starves `FeeVault` of protocol and creator revenue while `Zap`'s documented 0.75% fee is advertised to users as protocol policy.

**Uncertainty note:** I was not able to read the full body/modifiers of `Bonding.buy`/`Bonding.sell` before running out of tool iterations, so I cannot cite the exact access-control statement (or absence thereof) inside those function bodies. The finding rests on strong indirect evidence — the explicit architecture documentation stating fee logic was deliberately "moved to the router" [Zap] and that `Bonding`/`Router` hold "no fee logic," plus the `trader`-passthrough call signature from `Zap._buyOnCurve`/`_sellOnCurve` — rather than a directly observed missing-modifier. A background Devin session with full file access should verify the exact visibility and modifiers on `Bonding.buy`/`Bonding.sell` in `packages/contracts/src/Bonding.sol` to confirm whether any caller restriction exists before treating this as fully confirmed.

### Citations

**File:** docs/contracts-scope.md (L11-13)
```markdown
| `Bonding.sol` | Main entry — launch, buy, sell, graduation (no fee logic — moved to the router) |
| `Factory.sol` | Pair registry |
| `Router.sol` | AMM math, buy/sell execution (returns gross amounts; no fee deduction) |
```

**File:** packages/contracts/src/Zap.sol (L292-294)
```text
        uint256 buyFeeBps_ = $.buyFeeBps;
        uint256 feeOnGross = (usdcAmount * buyFeeBps_) / BPS_DENOM;
        uint256 netUsdc = usdcAmount - feeOnGross;
```

**File:** packages/contracts/src/Zap.sol (L454-459)
```text
        // Symmetric with `_executeBuy`: fee charged on EVERY sell — curve
        // AND post-graduation. The `isGraduated` branch above selects the
        // venue, not the fee policy. See `_executeBuy` for the rationale.
        uint256 fee = Math.mulDiv(grossUsdc, $.sellFeeBps, BPS_DENOM, Math.Rounding.Ceil);
        usdcOut = grossUsdc - fee;

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
