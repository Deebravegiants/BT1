### Title
Unsafe low-level `IERC20.transfer` calls in Tron `IntentGatewayV2` only check `success`, not the returned boolean, permitting silent transfer failures - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` uses raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` for escrow withdrawal, refund, and dust-sweep token payouts, checking only that the low-level `call` itself succeeded (`success`) without decoding/validating the returned boolean data. This is the exact non-safe-ERC20 pattern the referenced Cooler audit finding warns about: ERC20 implementations that return `false` on failure instead of reverting will make `success == true` even though no tokens were actually transferred.

### Finding Description
In `withdraw()`, `_filled` escrow release for solvers/beneficiaries is settled via: [1](#0-0) 
and fee payout: [2](#0-1) 
and the `SweepDust` handler in `onAccept`: [3](#0-2) 

In each case, only `success` (i.e. that the target contract did not revert / the call did not run out of gas) is checked. The ABI-encoded return data — which per the ERC20 standard should contain a `bool` indicating whether the transfer actually happened — is never decoded or checked. Non-compliant tokens (e.g., tokens that return `false` instead of reverting on failure, or tokens whose `transfer` call fails silently due to blacklisting, pausing, or insufficient balance edge cases) will make this code proceed as if the transfer succeeded.

Critically, before this raw call, accounting state is already mutated: `_orders[body.commitment][token] -= amount;` at line 710, and `delete _orders[body.commitment][TRANSACTION_FEES];` at line 722. If the underlying `transfer` call reports `success = true` while actually failing to move tokens (returning `false`), the escrow/fee balances are decremented/deleted without the beneficiary ever receiving funds — resulting in a stuck/lost claim with no reachable retry, since `_filled[body.commitment]` is already marked and `_orders` accounting is already reduced.

This contrasts with the mainline EVM `IntentGatewayV2.sol` and `IntentsBase.sol`, which consistently use `SafeERC20.safeTransfer`/`safeTransferFrom` (OpenZeppelin's safe wrapper that both checks `success` and validates return data), e.g.: [4](#0-3) 
The Tron contract imports `SafeERC20` and uses `using SafeERC20 for IERC20;` but does not actually apply it in these withdrawal/sweep paths, instead reverting to raw `.call` with a manual `success` check that omits the return-data validation `SafeERC20` provides.

### Impact Explanation
This is reachable by any solver or user interacting with the permissionless intents flow: a solver calls `fill`/`select` to fill an order, or a user's order is refunded/redeemed cross-chain via `onAccept` after a relayed `RedeemEscrow`/`RefundEscrow`/`SweepDust` message. If the input/output token used in the order is a non-standard ERC20 that returns `false` on failed transfers (rather than reverting), the beneficiary permanently loses their claim to the escrowed funds while the protocol's internal accounting (`_orders` mapping) is decremented as if payment succeeded — a permanent freezing/loss of user or solver funds with no compensating control. Given IntentGatewayV2's role as an intents escrow/settlement contract handling arbitrary caller-specified tokens (`order.inputs`/`order.output.assets`), this can affect any order using a non-conforming token.

### Likelihood Explanation
Likelihood is contingent on interaction with a non-standard ERC20 token (one that returns `false` rather than reverting on failure). This is a well-documented class of tokens on both EVM and TRON (e.g., certain TRC20 tokens do not strictly follow the boolean-return convention or can return `false` under specific conditions like blacklist/pause). Because `IntentGatewayV2` is designed to be generic, accepting arbitrary tokens in `order.inputs`/`order.output.assets`, any order configured with such a token is exposed. No malicious privileged actor is required — a normal order settlement, refund, or dust-sweep flow is sufficient to trigger the vulnerable code path.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` (lines 702-708, 716-722) and in the `SweepDust` handler (lines 670-676) with `SafeERC20.safeTransfer`, consistent with the rest of the codebase (`evm/src/apps/intentsv2/IntentsBase.sol`, `WrappedHyperFungibleToken.sol`). If Tron-specific ecosystem constraints require avoiding `SafeERC20` (e.g., some TRC20 tokens do not return data at all), explicitly decode and validate the returned data length/boolean (`success && (returndata.length == 0 || abi.decode(returndata, (bool)))`) rather than only checking `success`.

### Proof of Concept
1. Deploy a mock ERC20/TRC20 token whose `transfer` function returns `false` on failure instead of reverting (a common non-compliant token pattern).
2. Create and fill a cross-chain intent order (`Order`) using this token as an output/input asset via `IntentGatewayV2`.
3. Trigger settlement so that `onAccept` invokes `withdraw()` with `RedeemEscrow`/`RefundEscrow`, or so that Hyperbridge dispatches a `SweepDust` message.
4. Configure/mock the token so `transfer` returns `false` for the specific transfer call (e.g., beneficiary is blacklisted, or contract-specific failure condition).
5. Observe that:
   - `token.call(...)` returns `success = true` (the call itself doesn't revert) even though the internal `bool` return value is `false`.
   - The contract does NOT revert with `TransferFailed`, since only `success` is checked.
   - `_orders[body.commitment][token] -= amount` (or `delete _orders[...][TRANSACTION_FEES]`) executes, permanently reducing on-chain escrow/fee accounting.
   - The beneficiary never receives the tokens, and there is no way to reclaim them since the escrow entry is already marked filled/zeroed. [5](#0-4)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
