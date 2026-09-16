### Title
Unsafe ERC20 transfer in Tron `IntentGatewayV2::withdraw()` / `SweepDust` handling does not check the boolean return value - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron-specific `IntentGatewayV2` contract escrows input tokens safely via `SafeERC20.safeTransferFrom`, but the outbound token-release paths (`withdraw()` used by `RedeemEscrow`/`RefundEscrow`, and the `SweepDust` handler in `onAccept()`) use raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the external call did not revert — they never decode/verify the ERC20 boolean return value.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the contract imports and uses `SafeERC20` for escrowing user inputs (`IERC20(token).safeTransferFrom(...)`), [1](#0-0)  but the internal `withdraw()` function, which releases escrowed funds to a beneficiary on `RedeemEscrow`/`RefundEscrow`, performs a raw `.call` and only checks `success`: [2](#0-1) 

The same unsafe pattern is used in the `SweepDust` request handling inside `onAccept()`: [3](#0-2) 

`success` from a low-level `.call()` is only `false` if the call reverted; it does not reflect the ERC20 `transfer` function's returned boolean. Some non-standard ERC20 tokens return `false` on failure instead of reverting (e.g. certain legacy/non-compliant tokens, or tokens paused/blacklisting a recipient that choose to return `false`). Since the return data is never decoded here, such a failed transfer is silently treated as a success.

### Impact Explanation
In `withdraw()`, after the unchecked `.call`, the code unconditionally decrements the escrow accounting (`_orders[body.commitment][token] -= amount;`) and, on finalize, marks the order filled (`_filled[body.commitment] = beneficiary`) and emits `EscrowReleased`/`EscrowRefunded`. If the underlying token silently fails the transfer, the beneficiary receives no funds while the protocol's internal accounting reports the order as filled/refunded and the escrow balance as spent — resulting in a permanent loss of the escrowed funds (locked in the contract with no accounting entry left to reclaim them). The same class of issue applies to `SweepDust`, where accounting and events assume a successful sweep regardless of the actual transfer result.

This is reachable via a normal, permissionless flow: a relayer delivers an authenticated ISMP `RedeemEscrow`/`RefundEscrow`/`SweepDust` POST request to `onAccept()`, which is a legitimate cross-chain message-delivery path for the intents escrow, not requiring any privileged or malicious actor — it only requires a token that returns `false` on transfer failure to be configured/used as an order's input/output token.

### Likelihood Explanation
Likelihood depends on a token used within an order behaving non-standard (returning `false` instead of reverting on failed transfer, e.g., when the recipient is blacklisted/paused). This is a well-known real-world ERC20 quirk supported by several tokens; because the gateway is a generic multi-token intents system, users/solvers can select which token/output pairs to use for an order, and the escrow flow does not restrict eligible tokens to strictly-safe implementations elsewhere in this file's outbound paths, unlike its inbound escrow logic which correctly uses `safeTransferFrom`.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` branch of `onAccept()` with `SafeERC20.safeTransfer` (already imported and used elsewhere in the same file via `using SafeERC20 for IERC20;`), so that both call-reversion and false-boolean-return failures cause the outbound transfer to revert instead of being silently accepted as successful.

### Proof of Concept
1. An order is placed with an output/input token `T` that implements a non-reverting failure mode (returns `false` on `transfer` failure, e.g. recipient blacklisted).
2. A relayer delivers a valid ISMP `RedeemEscrow` message for a filled order whose beneficiary is blacklisted by token `T` (or `T`'s transfer otherwise fails without reverting).
3. `onAccept()` → `withdraw()` executes `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`; the call succeeds at the EVM level (`success == true`) even though `T` internally returns `false` and moves no tokens.
4. `_orders[body.commitment][token] -= amount` still executes and `_filled[body.commitment] = beneficiary` is set, emitting `EscrowReleased`.
5. The beneficiary never receives the `amount` of token `T`, and the escrow accounting no longer reflects any claim to it — the funds are permanently stuck/lost in the contract.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
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
