`onAccept` is `onlyHost`-gated, but the host itself calls it after a relayer delivers a verified ISMP proof — so any relayer can trigger `withdraw()` by delivering a `RedeemEscrow`/`RefundEscrow` message once `authenticate()` passes (source-chain authorization check on the request, not on who relays it). This is the same "unprivileged message dispatcher/relayer" reachability class the task requires.

## Title
Unchecked TRC20/ERC20 `transfer()` return value in `IntentGatewayV2.withdraw()` finalizes escrow release without guaranteeing token delivery - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed order funds via raw low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` calls and only checks the outer call's `success` boolean, never decoding and validating the ERC20/TRC20 `transfer()` return value itself. [1](#0-0) 

### Finding Description
`withdraw()` is invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` requests (and again from `onGetResponse()` for cancellations), after only an `authenticate()` check on the request body — not on who relays it, so any relayer delivering a valid ISMP proof can trigger it: [2](#0-1) [3](#0-2) 

Inside `withdraw()`, each escrowed token is released using:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
``` [4](#0-3) 

This exactly mirrors the reported bug class: `success` here only reflects whether the low-level call *reverted*, not whether the token's `transfer()` function itself returned `true`. Many ERC20/TRC20 tokens (including some deployed on Tron) return `false` on failure instead of reverting. When that happens, `success == true` even though no tokens moved, the function proceeds to decrement `_orders[body.commitment][token]` and mark `_filled[body.commitment] = beneficiary`, finalizing the withdrawal as if it succeeded. [4](#0-3) 

The same unchecked pattern is repeated for the fee-token transfer and for `SweepDust` in the same file: [5](#0-4) [6](#0-5) 

Notably, the mainline EVM contracts (`evm/src/apps/intentsv2/IntentsBase.sol` and `evm/src/apps/IntentGatewayV2.sol`) correctly use OpenZeppelin's `SafeERC20.safeTransfer`, which reverts on a falsy return value: [7](#0-6) 
This shows the Tron variant deliberately diverges from the safe pattern used elsewhere, reintroducing exactly the class of bug the audit report flagged.

### Impact Explanation
Escrowed order funds (or accumulated transaction fees) can be permanently lost: the contract marks the order as filled/refunded and zeroes out the internal `_orders` accounting even though the actual token transfer silently failed. Once `_orders[commitment][token]` is decremented and `_filled[commitment]` is set, there is no retry path — the escrow record is gone but the tokens remain stuck in the `IntentGatewayV2` contract, unrecoverable by the beneficiary. This is a direct, permanent loss-of-funds condition for solvers/users redeeming or being refunded escrow on Tron.

### Likelihood Explanation
Reachable by any relayer that delivers a `RedeemEscrow`/`RefundEscrow` POST request or a GET response proof — no privileged role is required beyond normal ISMP message delivery, which is the permissionless relayer duty. The trigger condition depends on the escrowed token (or fee token) being one whose `transfer()` can return `false` without reverting, which is a known, non-exotic behavior among TRC20/ERC20-style tokens, especially relevant on Tron where TRC20 semantics are less standardized than mainstream EVM ERC20s.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + outer-success-only check with OpenZeppelin's `SafeERC20.safeTransfer` (as already used in `evm/src/apps/intentsv2/IntentsBase.sol`), or explicitly decode and require the inner boolean return value (`success && (data.length == 0 || abi.decode(data, (bool)))`) before mutating `_orders` and `_filled` state, for every transfer call in `withdraw()`, the fee-token payout, and the `SweepDust` branch of `onAccept()`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with an escrow input token that returns `false` (rather than reverting) on a failed `transfer()` — e.g., a token that silently declines to transfer beyond a certain cap, or a paused/blacklisted-recipient token following the classic non-reverting ERC20 pattern.
2. A solver escrows this token via `newOrder`, then the order is filled and a `RedeemEscrow` (or cancelled and a `RefundEscrow`) request is dispatched back to the source chain.
3. Any relayer delivers the verified ISMP proof; `onAccept()` calls `authenticate()` (passes, since it only checks the request's source/commitment, not the relayer) and invokes `withdraw(body, ...)`.
4. Inside `withdraw()`, the low-level `token.call(...)` returns `success = true` (the call itself doesn't revert) while the token's internal logic returns `false` and transfers zero tokens to `beneficiary`.
5. `_orders[body.commitment][token] -= amount` and `_filled[body.commitment] = beneficiary` execute regardless, emitting `EscrowReleased`/`EscrowRefunded`. The beneficiary receives nothing, the escrow record shows the order as settled, and the tokens remain permanently stranded in the `IntentGatewayV2` contract.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```
