Found a valid analog in `BandwidthManager.sol`.

### Title
`BandwidthManager::purchase` underflows `10 ** (18 - dec)` when the fee token has more than 18 decimals - (File: evm/src/apps/BandwidthManager.sol)

### Summary
`purchase()` computes `uint256 scale = 10 ** (18 - dec)` where `dec` is the fee token's `decimals()` read directly from an arbitrary ERC20 (`IDispatcher(_host).feeToken()`). This is the same pattern as the reported Notional bug: `18 - dec` is evaluated as `uint8` arithmetic, so if `dec > 18` the subtraction underflows/wraps, producing a huge exponent that either reverts on `10 ** huge` (out-of-gas/overflow revert) or, if within range, yields a wildly wrong `scale`.

### Finding Description
In `evm/src/apps/BandwidthManager.sol`: [1](#0-0) 
```
uint256 price18d = tierPrice[tier];
if (price18d == 0) revert UnknownTier();

uint256 total18d = price18d * months;
address feeToken = IDispatcher(_host).feeToken();
uint8 dec = IERC20Metadata(feeToken).decimals();
uint256 scale = 10 ** (18 - dec);
if (total18d % scale != 0) revert PriceNotRepresentable();
uint256 amount = total18d / scale;
```
`dec` is a `uint8` fetched trustlessly from `feeToken().decimals()`. Solidity 0.8.17 checked-arithmetic reverts `18 - dec` when `dec > 18` (rather than silently wrapping as in the pre-checked-math Solidity used in the original Notional report), but the effect is the same class of bug: the assumption that ERC20 decimals are always ≤ 18 is unchecked, and any fee token configured with decimals > 18 (a real-world "weird ERC20" pattern) makes every `purchase()` call revert, permanently bricking the bandwidth-purchase path for that fee token. Unlike the original report where the bug silently underflows to a huge number, here the effect is a hard, permanent DoS of the purchase entrypoint because the checked subtraction reverts unconditionally whenever the fee token's decimals exceed 18.

This is reachable by any unprivileged caller/bandwidth purchaser: `purchase()` has no access control and is meant to be called directly by end users.

### Impact Explanation
If governance (via `onAccept`/`SetTiers`) or deployment configures a fee token with `decimals() > 18` — which is a legitimate, if unusual, ERC20 property — the `purchase()` function becomes permanently unusable: every call reverts at `10 ** (18 - dec)`. This is a route unable to deliver messages/complete payment: bandwidth can never be purchased for that fee-token configuration, i.e. a total freeze of the bandwidth purchasing functionality for the affected fee token, and the dispatch to `pallet-bandwidth` (`PALLET_BANDWIDTH_MODULE_ID`) can never occur.

### Likelihood Explanation
The fee token is set at the `IsmpHost` level (`IDispatcher(_host).feeToken()`), not controlled by `BandwidthManager` itself, so this triggers whenever the host's configured fee token happens to have `decimals() > 18`. This is plausible for a permissionless-deployment host/fee-token configuration change and does not require malicious governance — it is a straightforward misconfiguration/edge case that a normal fee-token swap could trigger, since nothing in `BandwidthManager` validates or bounds `dec`.

### Recommendation
Explicitly validate `dec <= 18` (and handle `dec > 18` correctly, e.g. by dividing instead of multiplying, similar to `adjustDecimals` in `sdk/packages/sdk/src/utils.ts`) before computing `scale`, or revert with a clear, named error (e.g. `UnsupportedFeeTokenDecimals`) rather than an implicit underflow/overflow revert:
```solidity
uint8 dec = IERC20Metadata(feeToken).decimals();
if (dec > 18) revert UnsupportedFeeTokenDecimals();
uint256 scale = 10 ** (18 - dec);
```

### Proof of Concept
1. Deploy `BandwidthManager` and configure a mock ERC20 fee token with `decimals() == 24` as the host's `feeToken()`.
2. Governance sets a tier price via `onAccept`/`SetTiers` ( [2](#0-1) ).
3. Call `purchase(app, tier, months, chain)` as any user.
4. The call reverts inside `10 ** (18 - dec)` because `18 - 24` underflows the `uint8`/`uint256` checked arithmetic, permanently blocking all purchases for this fee-token configuration.

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L160-170)
```text
        uint256 price18d = tierPrice[tier];
        if (price18d == 0) revert UnknownTier();

        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(_host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        uint256 scale = 10 ** (18 - dec);
        if (total18d % scale != 0) revert PriceNotRepresentable();
        uint256 amount = total18d / scale;

        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), amount);
```

**File:** evm/src/apps/BandwidthManager.sol (L213-219)
```text
        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.SetTiers) {
            Tier[] memory updates = abi.decode(request.body[1:], (Tier[]));
            for (uint256 i = 0; i < updates.length; i++) {
                tierPrice[updates[i].tier] = updates[i].price;
                emit TierSet(updates[i].tier, updates[i].price);
            }
```
