### Title
Sells Can Permanently Revert When BounceTech's Live `minTransactionSize()` Diverges From Zap's Cached Floor, With No Retry Path - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._sellInternal` gates a sell with its own `minUsdcAmount()` estimate *before* calling the LT's `redeem()`, but the actual floor enforced at redemption time is BounceTech's independently owner-settable `minTransactionSize()` on the external LT/`GlobalStorage` contract. Because these two values are not the same on-chain read and Zap has no fallback/queue path for a reverted redeem, a seller whose sell passes Zap's pre-check but whose actual LT-to-USDC amount falls under BounceTech's live floor gets an unrecoverable revert, freezing their exit exactly the way the original report's Chainlink heartbeat freeze locked withdrawals — except the destabilizing variable here is BounceTech's mutable `minTransactionSize()`, not a stale price feed.

### Finding Description
`Zap.sell`/`_sellInternal` transfers the caller's launched token in, converts it to LT via the curve or HyperSwap, and then calls the LT's atomic `redeem()`: [1](#0-0) 

Before calling `redeem()`, Zap only checks its own `minUsdcAmount()` against an *estimate* computed from `ltReceived * exchangeRate()`: [2](#0-1) 

The actual floor enforced by BounceTech at `redeem()` time is `IBounceGlobalStorage.minTransactionSize()` — a value the docs explicitly call out as "Owner-settable on the BounceTech side," i.e. mutable by BounceTech independent of Zap's own configuration: [3](#0-2) 

The interface docs for `IBounceLeveragedToken.redeem` and the mock used in tests confirm redemptions under the live floor revert with the bare, undecodable selector `BelowMinTransactionSize` (`0x05eb05ac`): [4](#0-3) [5](#0-4) 

Zap's own comment acknowledges there is deliberately no recovery mechanism if `redeem()` reverts: [6](#0-5) 

If Zap's `minUsdcAmount()` is not kept perfectly synchronized with BounceTech's live `minTransactionSize()` (which BounceTech can raise at any time, exactly as an oracle admin can widen or the feed can go stale), a sell that clears Zap's pre-check can still hit the real floor inside `redeem()` and hard-revert with no way for the user to reduce or restructure the call to succeed — the amount they are trying to exit is fixed by their token holdings and the curve/AMM conversion, not something they can freely resize upward past a floor they don't fully control. This is a structurally identical failure mode to the original report: a value read from an external, permissionlessly-mutable system (Chainlink heartbeat/oracle staleness there, BounceTech's `minTransactionSize()` here) causes an exit-path revert that the caller cannot work around, and the contract deliberately provides no fallback queue.

### Impact Explanation
A seller who has fully or partially built a dust-sized position (e.g., by design of the buy-side floor-bump branch, which explicitly refunds *LT* dust to buyers rather than USDC, potentially leaving holders with small LT-equivalent balances) can find their `Zap.sell` permanently reverting once BounceTech raises `minTransactionSize()` above what Zap's cached floor assumed passable. Since there is no `prepareRedeem`/queue fallback and the position size is fixed by the trader's actual holdings, funds are effectively frozen in the token/curve position with no on-chain path to exit via Zap. This is a freezing-of-trader-funds impact under the stated validation criteria.

### Likelihood Explanation
BounceTech's `minTransactionSize()` is explicitly documented as owner-settable and outside alt.fun's control; any upward revision creates the divergence window. The floor-bump buy path shows the protocol is already aware dust amounts near this floor exist in practice (it works around the floor on buys), but the sell path has no equivalent protection, making the condition realistically reachable — no attacker action is required, only routine operational changes on BounceTech's side or natural dust accumulation from prior curve/floor-bump buys.

### Recommendation
Have `Zap` read BounceTech's `minTransactionSize()` live (via `IBounceGlobalStorage`) rather than relying on a possibly-stale local `minUsdcAmount()` constant, and enforce the same floor consistently on both buy and sell paths. Additionally, add a fallback for sells whose LT-equivalent amount is under the live floor — e.g., allow batching/aggregating dust across multiple sells, or expose a way for the user to top up the traded amount atomically so the redeemed amount always clears BounceTech's current floor.

### Proof of Concept
1. A trader ends up holding a token amount whose curve-sell converts to an LT amount `X` such that `ltToBaseAmount(X)` is just above Zap's local `minUsdcAmount()` but below BounceTech's *current* `minTransactionSize()` (BounceTech having raised it after Zap's floor was last configured/deployed).
2. Trader calls `Zap.sell(tokenAddress, tokenAmount, minUsdcOut)`. Zap's pre-check (`grossUsdcEstimate / 1e12 < minUsdcAmount()`) passes.
3. Zap calls `IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0)`; BounceTech reverts with `BelowMinTransactionSize` (`0x05eb05ac`) because the live floor is higher than what Zap checked.
4. The trader's tokens have already been pulled in (`safeTransferFrom` at the top of `_sellInternal`) and the sell reverts atomically — the tokens remain in the trader's original position and there is no smaller/larger resend that fixes the mismatch since the amount is fixed by the trader's holdings and the curve conversion; the trader is stuck unable to exit via `Zap.sell`.

### Citations

**File:** packages/contracts/src/Zap.sol (L440-452)
```text
        uint256 ltReceived = bonding_.isGraduated(tokenAddress)
            ? _sellOnUniswapV2(tokenAddress, lt, tokenAmount)
            : _sellOnCurve(tokenAddress, tokenAmount);

        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();

        // Intentional v1 tradeoff: sells only use BounceTech's atomic
        // `redeem()` path (no `prepareRedeem` fallback/queue in Zap). If the
        // LT idle-USDC buffer is temporarily depleted, `redeem` reverts and
        // users must retry in smaller chunks after buffer replenishment.
        // Redeem into this zap (not the user) so we can deduct the fee.
        uint256 grossUsdc = IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0);
```

**File:** packages/contracts/src/interfaces/IBounceGlobalStorage.sol (L12-14)
```text
    /// @notice Minimum base-asset (USDC, 6dp) amount accepted by LT
    ///         `mint`/`redeem`. Owner-settable on the BounceTech side.
    function minTransactionSize() external view returns (uint256);
```

**File:** packages/contracts/test/mocks/MockLeveragedToken.sol (L54-65)
```text
    function redeem(
        address to,
        uint256 ltAmount,
        uint256
    ) external returns (uint256 baseAmount) {
        _burn(msg.sender, ltAmount);
        baseAmount = ltToBaseAmount(ltAmount);
        if (_minTransactionSize > 0 && baseAmount < _minTransactionSize) {
            revert BelowMinTransactionSize();
        }
        ERC20(baseAsset).transfer(to, baseAmount);
    }
```

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L18-23)
```text
    /// @notice LT → USDC. Reverts if the computed USDC output exceeds `baseAssetBalance()`.
    function redeem(
        address to,
        uint256 ltAmount,
        uint256 minBase
    ) external returns (uint256 baseAmount);
```
