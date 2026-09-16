## Analysis

The reported bug class — unchecked/unsafe token-transfer handling leading to inconsistent, unrecoverable escrow state — has a direct analog in `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `withdraw()` function, which is the escrow-release path reachable by any relayer delivering a `RedeemEscrow`/`RefundEscrow` message (`onAccept`) or a cancellation storage proof (`onGetResponse`).

### Title
Unchecked ERC20/TRC20 return value in `IntentGatewayV2.withdraw()` permanently freezes escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()` transfers escrowed input/fee tokens using a raw low-level `.call` to `IERC20.transfer`, and only checks that the *call itself* did not revert (`success`). It never decodes/validates the boolean return value that a compliant ERC20/TRC20 `transfer` is supposed to return. Immediately afterwards, regardless of whether the token silently returned `false`, the function decrements the escrow accounting and marks the order `_filled`, then emits `EscrowReleased`/`EscrowRefunded`.

### Finding Description
`withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol`: [1](#0-0) 

For each escrowed token it does:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
```
This only reverts if the low-level call itself reverts. A token contract whose `transfer` function returns `false` (rather than reverting) on failure — which is exactly the class of non-standard token that Tron's TRC20 ecosystem is well known to contain, and which the escrowed `order.inputs[i].token` addresses are fully attacker-controlled at `placeOrder` time — will make `success == true` while no tokens actually move. The function then proceeds to zero out `_orders[commitment][token]` and (on `finalize`) set `_filled[commitment] = beneficiary`, permanently marking the order as settled.

This is the exact same class of defect flagged in the source report: "Token Transfer Failure Handling... lacks comprehensive error handling" and "Partial Failure on Transfer... may lead to inconsistent reward/escrow tracking." Notably, the rest of the same contract (`placeOrder`, at lines 405/459/484) and the canonical EVM implementation `IntentsBase.sol::_withdraw` use OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom` (which decodes and validates return data), showing this raw-call path in the Tron variant's `withdraw()` is an inconsistency/regression rather than an intentional design choice: [2](#0-1) [3](#0-2) [4](#0-3) 

The identical unchecked pattern is also used for the fee-token payout and for `SweepDust`: [5](#0-4) [6](#0-5) 

### Impact Explanation
Because escrow accounting is decremented and the order is marked `_filled` even when the underlying token transfer silently failed, the tokens remain trapped in the `IntentGatewayV2` contract with no remaining code path to recover them (`_orders[commitment][token]` is already zero, so any retry hits `UnknownOrder()`, and `_filled` blocks any future fill/cancel). This is a permanent freezing of escrowed user/solver funds — reachable from a single relayer-delivered `RedeemEscrow`/`RefundEscrow` message or a GET-response cancellation, both of which are standard, permissionless flows in the Intent Gateway.

### Likelihood Explanation
The escrowed token address is fully attacker-controlled: a user places an order (`placeOrder`) with an arbitrary ERC20/TRC20 as an input token. If that token (or any third-party token whose behavior changes, e.g., via a pausable/blacklist mechanism that returns `false` instead of reverting) fails to transfer during `withdraw()`, the failure is silently swallowed. No privileged role is required to trigger the withdraw path — it fires automatically whenever a relayer delivers the settlement/refund message, which is the normal, expected operation of the protocol.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` (and in the `SweepDust` handler) with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the rest of the contract (`placeOrder` already imports and uses `SafeERC20`). `safeTransfer` correctly reverts on both a reverting call and a call that returns `false`/malformed data, ensuring escrow state is only mutated after a confirmed successful transfer.

### Proof of Concept
1. Attacker deploys a token `EvilToken` whose `transfer()` returns `false` (no revert) whenever a certain internal condition is met (e.g., after N calls, or controlled by an owner-settable flag), and `true` otherwise.
2. Attacker calls `placeOrder()` on `IntentGatewayV2` (Tron) using `EvilToken` as an escrowed input, funding the escrow normally.
3. When the order is filled/cancelled and settlement is delivered via `onAccept`/`onGetResponse`, `withdraw()` calls `EvilToken.transfer(beneficiary, amount)`, which returns `false` but does not revert.
4. `success` is `true` (the call did not revert), so `if (!success) revert TransferFailed();` does not trigger.
5. `_orders[commitment][token] -= amount` zeroes the escrow record, and `_filled[commitment] = beneficiary` is set; `EscrowReleased`/`EscrowRefunded` is emitted.
6. The beneficiary receives no tokens, and the tokens are now stuck in the `IntentGatewayV2` contract with no accounting path to withdraw them — permanent loss of the escrowed funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L455-460)
```text
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }
```

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
