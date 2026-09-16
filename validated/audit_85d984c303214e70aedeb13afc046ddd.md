This confirms the analog. Let me get the full list of usages and check `onAccept` (settlement entry point) to confirm reachability via an unprivileged relayer-delivered message.### Title
Silent ERC20 transfer failure bypasses accounting in Tron IntentGatewayV2 `withdraw`/`sweepDust`/`SweepDust` handlers, permanently freezing/misreporting escrow - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` settles escrow releases, dust sweeps, and fee payouts using raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks that the *call itself* did not revert (`success`), never decoding/checking the ERC20 `transfer` boolean return value. This is the same bug class as the referenced D3Vault finding: accounting state is updated on the assumption that a token movement succeeded, when in fact a standards-compliant ERC20 that returns `false` on failure (instead of reverting) would leave `success == true` while no tokens actually moved.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `withdraw()` (the internal settlement function invoked from `onAccept` when a `RedeemEscrow`/`RefundEscrow` message arrives from the source/destination gateway via Hyperbridge, and from `onGetResponse` for cross-chain cancellation) does: [1](#0-0) 

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();

_orders[body.commitment][token] -= amount;
```

`success` only reflects whether the external call reverted; it does not inspect the returned `bool` from `transfer()`. Per EIP-20, a compliant token is permitted to return `false` instead of reverting when a transfer cannot be completed (e.g., insufficient balance held by the gateway due to prior dust-sweep miscalculation, a paused/blacklisted state, or any conditional-failure token). In that case the low-level call succeeds (`success == true`) even though zero tokens were moved to `beneficiary`, yet the code proceeds to decrement `_orders[body.commitment][token]` as if the funds were delivered [2](#0-1) .

The same unchecked-return-value pattern recurs for:
- The transaction-fee payout inside the same `withdraw()` function [3](#0-2) .
- The `SweepDust` ISMP request handler, which pays out swept dust to a beneficiary and emits `DustSwept` regardless of whether the underlying transfer actually moved tokens [4](#0-3) .

Note that elsewhere in the codebase (the canonical EVM `IntentsBase.sol` and `HyperFungibleToken`/`HyperFungibleTokenUpgradeable`) this exact class of bug is avoided by using OpenZeppelin's `SafeERC20.safeTransfer`, which decodes and validates the boolean return value and reverts on failure [5](#0-4) . The Tron variant of `IntentGatewayV2` diverges from this safe pattern for its settlement/withdraw path, reintroducing the vulnerability class the rest of the codebase deliberately guards against.

### Impact Explanation
`withdraw()` is the terminal step of the Intent Gateway's cross-chain settlement flow: it is reached whenever Hyperbridge delivers a `RedeemEscrow` (solver claim after a cross-chain fill) or `RefundEscrow`/GET-response cancellation message to `onAccept`/`onGetResponse`. If the escrowed token silently fails to transfer (returns `false`), the protocol will:
- Decrement the internal escrow ledger (`_orders[commitment][token] -= amount`) even though the solver/user never received the tokens, permanently freezing those funds in the gateway contract with no ledger entry left to reclaim them.
- Mark the order as filled/refunded (`_filled[body.commitment] = beneficiary`) and emit `EscrowReleased`/`EscrowRefunded`, making the loss unrecoverable through the normal order lifecycle since the commitment can never be re-settled.
- Similarly, `SweepDust` and the fee payout can under-report token loss to whichever beneficiary/treasury they route to, again with no on-chain trace once the escrow/fee entry is zeroed.

This constitutes permanent freezing of user/solver funds and an accounting desync between actual custody and recorded escrow — a High severity impact, directly analogous to the reported D3Vault issue where a failed transfer still updated borrow-repayment bookkeeping.

### Likelihood Explanation
Reachability requires only a standard token that returns `false` on failure rather than reverting (a common, EIP-20-compliant behavior, e.g. many custom/DeFi tokens, some rebasing/pausable/blacklist-capable tokens) being used as an order's input token, plus any ordinary condition causing the transfer to fail at settlement time (e.g., gateway's actual token balance falling short of the recorded escrow amount because of prior fee-on-transfer/dust-accounting edge cases, or the beneficiary becoming blacklisted/paused on the token). No privileged role is required — a normal user or solver placing/filling an order with such a token, and a relayer delivering the resulting ISMP message, is sufficient to hit this code path.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` (in `withdraw()` for both escrowed tokens and fees, and in the `SweepDust` handler) with OpenZeppelin's `SafeERC20.safeTransfer`, mirroring the approach already used in `evm/src/apps/intentsv2/IntentsBase.sol`. `SafeERC20` decodes the boolean return value (when present) and reverts on `false`, ensuring escrow/fee accounting is only ever decremented after a provably successful transfer.

### Proof of Concept
1. Deploy an ERC20 token whose `transfer()` returns `false` on failure instead of reverting (standard, spec-compliant behavior) and use it as an order's input token in `placeOrder` on the Tron `IntentGatewayV2`.
2. Arrange for the gateway's actual balance of that token to be insufficient at settlement time relative to the escrowed amount recorded in `_orders[commitment][token]` (e.g., via a discrepancy introduced by fee/dust handling, or a token that can be paused/blacklisted for the beneficiary between escrow and settlement).
3. Trigger settlement: solver fills the order cross-chain, and the relayer delivers the resulting `RedeemEscrow` message to `onAccept`, which calls `withdraw()`.
4. Inside `withdraw()`, `token.call(...)` returns `(true, encoded(false))` — the low-level call succeeds, so `success == true` and the `TransferFailed` revert is skipped, even though no tokens were transferred to `beneficiary`.
5. `_orders[body.commitment][token] -= amount` executes, the order is marked filled/refunded, and `EscrowReleased`/`EscrowRefunded` is emitted — while the beneficiary received zero tokens, and the escrow accounting can no longer be used to recover the loss. [6](#0-5)

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
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
