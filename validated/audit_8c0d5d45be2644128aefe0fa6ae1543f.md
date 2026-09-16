### Title
Unsafe raw low-level `IERC20.transfer` calls without return-value verification in Tron IntentGatewayV2's `withdraw`/`onAccept` (SweepDust) — silent-failure token settlement can desync escrow accounting - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`evm/tron/contracts/apps/IntentGatewayV2.sol` settles escrowed intent funds using a raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks that the call did not revert (`success`), never inspecting the ERC-20 return value. This is the same unsafe-`transfer`/`transferFrom` bug class described in ETRP-1: any ERC-20 whose `transfer` returns `false` on failure instead of reverting will make the gateway believe settlement succeeded, while it silently did not deliver funds — yet the on-chain escrow ledger is still decremented and success events are emitted. The parallel, non-Tron EVM contract (`evm/src/apps/intentsv2/IntentsBase.sol`) already fixed this exact class by using OpenZeppelin's `SafeERC20.safeTransfer`, confirming the Tron variant is a regression/unfixed analog of the same bug.

### Finding Description
In `withdraw()`:
```solidity
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}
_orders[body.commitment][token] -= amount;
``` [1](#0-0) 

and the fee-token redemption in the same function: [2](#0-1) 

and the `SweepDust` handler inside `onAccept`: [3](#0-2) 

All three sites treat a low-level `call` that merely doesn't revert (`success == true`) as proof of a successful transfer. They never decode/verify the ABI-encoded `bool` return value that ERC-20's `transfer` is supposed to return. Some ERC-20 implementations (particularly ones that don't strictly follow the standard, or wrapped/rebasing tokens) return `false` on failure (e.g., attempting to move more than an internal cap, or hitting a blacklist/pausable check) rather than reverting. With such a token, `success` from the raw `.call` remains `true` (since the callee didn't revert), so the `if (!success) revert TransferFailed();` guard is bypassed even though no tokens moved.

`withdraw()` is invoked from `onAccept` for `RequestKind.RedeemEscrow` / `RequestKind.RefundEscrow`, which is dispatched by an authenticated peer `IntentGateway` instance and delivered by any relayer submitting a valid ISMP proof — an unprivileged, permissionless path from the perspective of the relayer/solver that triggers the delivery: [4](#0-3) 

This contrasts with the corrected pattern already present in the non-Tron gateway's shared base contract, which uses `SafeERC20.safeTransfer`: [5](#0-4) 

### Impact Explanation
When settling escrow for a token whose `transfer` can return `false` without reverting: `_orders[body.commitment][token] -= amount;` still executes, permanently erasing the escrow record for that commitment even though the beneficiary received nothing. The tokens remain trapped in the `IntentGatewayV2` contract's balance with no accounting entry pointing to them, and `EscrowReleased`/`EscrowRefunded` is emitted as if settlement succeeded — resulting in a permanent freezing/loss of the user's or solver's escrowed funds. Because escrow amounts across all orders share the same contract-wide token balance, this desync can also under-collateralize the shared pool, jeopardizing other users' still-pending withdrawals of the same token. This satisfies the "permanent freezing of funds" / "unsound state commitment" impact bar.

### Likelihood Explanation
Triggering this only requires a token used as an intent input/output/fee-token to be one whose ERC-20 implementation returns `false` on failure instead of reverting — a well-documented and non-exotic class of tokens. No malicious admin/governance action is needed; a normal solver placing/filling an order in such a token (or the token later entering a state where transfer legitimately fails, e.g. paused or blacklisted recipient) is sufficient to hit the silent-failure path through the standard `RedeemEscrow`/`RefundEscrow`/`SweepDust` flows reachable by any relayer delivering a valid proof.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` (in `withdraw()` for both token and fee-token payouts, and in the `SweepDust` branch of `onAccept`) with OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, matching the fix already applied in `evm/src/apps/intentsv2/IntentsBase.sol`. This ensures both call-revert and boolean-false failure modes correctly abort the transaction before escrow accounting is mutated.

### Proof of Concept
1. Deploy (or use) an ERC-20 token whose `transfer` function returns `false` on failure (e.g., insufficient allowance/cap/blacklist) instead of reverting, and register it as an intent input token.
2. A user places an order with this token as input; it is escrowed into `IntentGatewayV2` via `placeOrder`.
3. Put the token into a state where `transfer(beneficiary, amount)` would return `false` for the escrow beneficiary (e.g., beneficiary is blacklisted, or a supply/allocation cap is hit).
4. A relayer submits a valid cross-chain proof invoking `onAccept` with `RequestKind.RedeemEscrow`, which calls `withdraw()`.
5. `token.call(...)` succeeds (no revert) but internally the token's `transfer` returned `false` — no tokens are moved to `beneficiary`.
6. `_orders[body.commitment][token] -= amount` still executes and `EscrowReleased` is emitted, permanently erasing the escrow record while the beneficiary received zero tokens — funds are stuck unrecoverably in the contract.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-681)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-710)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
