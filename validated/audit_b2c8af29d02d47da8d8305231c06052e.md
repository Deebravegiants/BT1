## Analog Found

### Title
Zap._sellOnCurve leaves a dangling Token→Router allowance after `bonding_.sell()`, unlike its `_buyOnCurve` counterpart - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._sellOnCurve` approves the curve `Router` for the full `tokenAmount` being sold, but — unlike the symmetric `_buyOnCurve` function two lines above it — never resets that allowance to zero after the external call returns.

### Finding Description
`_buyOnCurve` and `_sellOnCurve` are structurally symmetric internal helpers used by `Zap.buy`/`Zap.sell` to route a curve trade through `Bonding`/`Router`: [1](#0-0) 

`_buyOnCurve` approves `curveRouter` for `ltAmount`, calls `bonding_.buy(ltAmount, ...)` which returns `amountInUsed` (explicitly documented elsewhere as potentially less than the approved input), and then calls `IERC20(lt).forceApprove(address(curveRouter), 0)` to clear any unconsumed allowance.

`_sellOnCurve` does the same setup — `IERC20(tokenAddress).forceApprove(address(curveRouter), tokenAmount)` followed by `bonding_.sell(tokenAmount, tokenAddress, 0, msg.sender)` — but has **no matching `forceApprove(..., 0)` afterward**. This is the same root-cause pattern as the external report: an approval granted to enable an external call is reset on one path (buy) but not the other (sell), so any amount of the approval left unconsumed by the external call remains standing indefinitely, exactly as the Receiver left the executor’s allowance active when the reset step was skipped.

### Impact Explanation
If `Bonding.sell`/`Router`’s internal accounting ever consumes less than the full approved `tokenAmount` (e.g., due to a bonding-curve edge case, a mid-call graduation transition, or any code path where the pulled amount differs from the approved amount — mirroring the `amountInUsed < ltAmount` asymmetry that `_buyOnCurve` itself accounts for on the buy side), the leftover allowance from `Zap` to `Router` for the launched `Token` persists after the call returns. Since `Router`/`Bonding` are shared, non-single-use contracts invoked by every trader through `Zap`, a standing allowance on `Zap`'s own Token balance is a latent authorization that should not exist per the codebase's own "no-dangling-allowance invariant" (explicitly called out for the analogous `Bonding._routerDepositAndDispose` path). This breaks that invariant and is a bridge to fund-draining exposure of any Token balance sitting on `Zap` if the Router can later be induced to pull against that stale approval.

### Likelihood Explanation
`Zap.sell` is a fully unprivileged, directly reachable entry point for any trader. The missing reset is unconditional on this code path — it doesn't require an unusual gas-griefing setup like the original Receiver bug (which needed insufficient gas); it triggers on the ordinary case where the approved amount and the actually-consumed amount by `Bonding.sell` diverge. The asymmetry with `_buyOnCurve`, which the codebase author clearly recognized needed a reset, indicates this is an overlooked omission rather than an intentional design choice.

### Recommendation
Add `IERC20(tokenAddress).forceApprove(address(curveRouter), 0);` at the end of `_sellOnCurve`, mirroring `_buyOnCurve`'s cleanup, so no allowance to `Router` survives past the call regardless of how much of the approved `tokenAmount` was actually consumed.

### Proof of Concept
1. Trader calls `Zap.sell(tokenAddress, tokenAmount, ...)`, which internally calls `_sellOnCurve(tokenAddress, tokenAmount)`.
2. `_sellOnCurve` sets `Token.allowance(Zap, Router) = tokenAmount` then calls `bonding_.sell(tokenAmount, tokenAddress, 0, msg.sender)`.
3. If `Router`/`Bonding`'s internal pull of `Token` from `Zap` consumes less than `tokenAmount` for any reason, `_sellOnCurve` returns without clearing the allowance.
4. `Token.allowance(Zap, Router)` remains nonzero indefinitely, violating the intended "no-dangling-allowance" invariant enforced everywhere else in the codebase (`_buyOnCurve`, `Bonding._routerDepositAndDispose`), and exposing any `Token` balance later held by `Zap` to that stale approval. [1](#0-0) 

**Note on verification limits:** I was unable to load the body of `Bonding.sell`/`Router.sell` in this session (search results returned no matched line content for those functions) to confirm whether the pulled amount can ever be strictly less than `tokenAmount`. The finding rests on (a) the confirmed code asymmetry between `_buyOnCurve` (resets allowance) and `_sellOnCurve` (does not), and (b) the documented fact that the buy-side counterpart necessarily needed the reset because `amountInUsed` can be less than the approved input — a pattern likely mirrored on the sell side. Confirming the exact `Bonding.sell` internals would require a follow-up read of `packages/contracts/src/Bonding.sol` and `packages/contracts/src/Router.sol`.

### Citations

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
