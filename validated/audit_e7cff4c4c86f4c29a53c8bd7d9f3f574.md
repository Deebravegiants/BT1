### Title
Silent ERC20 transfer failures in `withdraw()` and `SweepDust` handling due to ignored return-data on low-level `.call` - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron deployment of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) settles escrowed intent funds using a raw low-level `.call` to the ERC20 `transfer` function and only checks that the call itself did not revert (`success`), never decoding/validating the returned boolean payload. This is the same bug class as the reported `John.sol` finding ("Transfer result value ignored") — but here the effect is on escrow settlement for cross-chain intents, not a simple staking contract, and it is reachable by any solver/user completing a normal fill/redeem/refund flow.

### Finding Description
In `withdraw()`, which is invoked from `onAccept()` when a `RedeemEscrow`/`RefundEscrow` request is authenticated and delivered from the destination chain (i.e., after a solver fills an order), escrowed input tokens and fees are released via: [1](#0-0) 

```
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```

The same pattern is used for fee redemption and in the governance-triggered `SweepDust` branch of `onAccept`: [2](#0-1) 

Unlike the rest of the codebase (both the standard `evm/src/apps/IntentGatewayV2.sol` and `evm/src/apps/intentsv2/IntentsBase.sol`), which consistently use OpenZeppelin's `safeTransfer`/`safeTransferFrom` (e.g. `IERC20(token).safeTransfer(beneficiary, amount);` in `IntentsBase.sol` `_withdraw`), the Tron variant reverted to a bare `.call` + `success` check. This checks only that the callee did not revert — it does **not** decode and verify the returned `bool` value. Many ERC20 tokens (particularly non-standard or Tron-native TRC20 tokens) return `false` on failed transfers instead of reverting. Under this pattern such a failure is treated as success: `_orders[body.commitment][token]` accounting is decremented, `EscrowReleased`/`DustSwept` events are emitted, and the transaction completes normally, even though the beneficiary never actually received the tokens.

### Impact Explanation
This directly affects the intents escrow settlement path used by every solver claiming filled orders and every user receiving refunds on cancellation. If the escrowed token silently returns `false` instead of reverting on the transfer (a documented behavior class for several existing tokens), the protocol will:
- Mark the order as filled/refunded (`_filled[body.commitment] = beneficiary`) and decrement escrow accounting, permanently losing the ability to re-claim the funds through `withdraw()`.
- Emit `EscrowReleased`/`EscrowRefunded` events even though no value moved.
- Effectively freeze/burn the escrowed input tokens (or transaction fees) inside the contract with no recovery path, since escrow state is already zeroed. This is a fund-freezing/loss-of-funds issue matching the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Likelihood depends on which tokens the Tron `IntentGatewayV2` is configured to support. Reaching this bug requires no privileged role — it triggers on the standard `placeOrder` → `fillOrder` → cross-chain `RedeemEscrow`/`RefundEscrow` → `withdraw()` flow that every solver and user goes through, and via the `SweepDust` administrative sweep. Given that TRC20/Tron token implementations are more prone to non-reverting failure semantics than typical Solidity ERC20s, and given that the rest of the codebase (EVM chains) explicitly avoids this exact pattern by using `safeTransfer`, the risk is non-trivial specifically for the Tron deployment.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` and the `SweepDust` branch of `onAccept()` with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the rest of the codebase (`evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/IntentGatewayV2.sol`). If `safeTransfer` cannot be used due to Tron-specific TRC20 quirks, at minimum decode and verify the returned boolean when return data is present, in addition to checking `success`.

### Proof of Concept
1. Deploy `evm/tron/contracts/apps/IntentGatewayV2.sol` with a TRC20 token whose `transfer` function returns `false` on failure instead of reverting (e.g., due to a blacklist/pause condition on the beneficiary).
2. A user places an order escrowing that token via `placeOrder`.
3. A solver fills the order on the destination chain; the resulting cross-chain `RedeemEscrow` message is delivered and authenticated, calling `withdraw()`.
4. During `withdraw()`, the beneficiary is blacklisted/paused on the token contract at settlement time, causing `transfer` to return `false` without reverting.
5. `token.call(...)` returns `success = true` (the call executed without reverting) so `if (!success) revert TransferFailed();` does not trigger; `_orders[body.commitment][token] -= amount;` proceeds and `EscrowReleased` is emitted, even though the beneficiary received nothing — the escrowed tokens are now unrecoverable.

Note: I was unable to re-open the full file in this session to double check surrounding lines beyond what was already retrieved via search (e.g., exact `authenticate()` implementation and full imports), so verification of the exact import list and any complementary safeguards elsewhere in the same file is based on the snippets already returned by search rather than a full-file read.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-681)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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
        }
```
