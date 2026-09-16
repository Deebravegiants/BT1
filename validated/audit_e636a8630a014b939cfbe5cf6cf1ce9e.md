Found a directly analogous issue in the Tron variant of `IntentGatewayV2.sol`. This is the same bug class as the report — the code checks that the low-level `.call()` itself didn't revert, but never inspects/decodes the returned boolean from the ERC20 `transfer()` call, so a token that returns `false` on failure (rather than reverting) is silently treated as a successful transfer while escrow/fee accounting is updated as if funds were paid out.

### Title
Unchecked ERC20 `transfer()` return value in `IntentGatewayV2.withdraw` and `onAccept` (SweepDust) leads to incorrect escrow accounting - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
In the Tron build of `IntentGatewayV2`, escrow redemption/refund (`withdraw`) and dust sweeping (`onAccept`, `RequestKind.SweepDust`) transfer ERC20 tokens using a raw low-level `.call()` with the `IERC20.transfer` selector, and only check that the call itself did not revert (`success`). They never decode/verify the boolean return data that the ERC20 standard `transfer()` function returns. Non-reverting tokens that return `false` on a failed transfer will pass this check, causing the contract to update accounting state (`_orders[...]` decrements, `TRANSACTION_FEES` deletion) and emit success events even though no tokens were actually delivered.

### Finding Description
`withdraw()` is invoked from `onAccept()` for `RequestKind.RedeemEscrow`/`RefundEscrow` requests, which arrive via a relayed, verified ISMP `PostRequest` delivered by the `IsmpHost` (`onlyHost` modifier) [1](#0-0) .

Inside `withdraw`, for every escrowed token the contract does:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
``` [2](#0-1) 

and for fees:
```solidity
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
delete _orders[body.commitment][TRANSACTION_FEES];
``` [3](#0-2) 

The `SweepDust` handler in `onAccept` has the identical pattern:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [4](#0-3) 

`success` here is only `true` if the callee didn't revert; it says nothing about the ABI-encoded boolean return value of `transfer()`. Any ERC20 (or TRC20, which the Tron variant targets) that returns `false` instead of reverting on failure — e.g., due to a paused/blacklisted transfer, insufficient balance in a non-standard implementation, or a fee-on-transfer/permissioned token — will make `success == true` while no tokens move. The contract nonetheless decrements `_orders[commitment][token]`, deletes the fee entry, marks `_filled[commitment] = beneficiary`, and emits `EscrowReleased`/`EscrowRefunded`. Note the same file elsewhere correctly uses `SafeERC20.safeTransferFrom` (which does perform this check) for escrow deposits, but the withdrawal/sweep paths were written with raw `.call()` instead of `safeTransfer`, despite `using SafeERC20 for IERC20;` being declared in the contract [5](#0-4) .

### Impact Explanation
Because `_filled[body.commitment]` is set and `_orders[...]` is decremented/deleted regardless of whether the token transfer actually succeeded, the escrowed tokens become permanently unreachable: the order is marked as filled/refunded so it cannot be retried, yet the beneficiary never received the funds. This is a permanent freezing/loss of user/solver escrowed funds — the exact same root cause as the reported `FootiumPrizeDistributor.claimERC20Prize` issue (state updated as if a transfer succeeded, without checking its actual outcome).

### Likelihood Explanation
This is reachable by any relayer delivering a legitimately-verified `RedeemEscrow`/`RefundEscrow`/`SweepDust` POST request once any escrowed token behaves non-standard-compliant (returns `false` rather than reverting) — a known and common real-world ERC20/TRC20 pattern, not requiring any privileged or malicious actor. The whole point of the check (`if (!success) revert`) demonstrates the author intended to guard against failed transfers but implemented an incomplete check, making this a straightforward, easily-triggered coding defect rather than a theoretical edge case.

### Recommendation
Replace the raw `.call()` + `success`-only check with `SafeERC20.safeTransfer` (already imported/used elsewhere in the same contract), which decodes and validates the boolean return value (or absence of it) per EIP-20/ERC-20 semantics:
```solidity
IERC20(token).safeTransfer(beneficiary, amount);
```
Apply this to `withdraw()` (both the token loop and the fee transfer) and to the `SweepDust` branch of `onAccept()`. If a raw call must be kept for Tron-specific TRC20 compatibility, at minimum decode and require the boolean return value when data is returned, mirroring `SafeERC20`'s logic.

### Proof of Concept
1. A user places an order on the source chain whose `inputs`/fee token is a non-standard ERC20/TRC20 deployed on the Tron destination, one that returns `false` (rather than reverting) when `transfer` fails (e.g., a paused token, or an implementation with an internal balance/allowance edge case).
2. The order proceeds normally; escrow accounting records `_orders[commitment][token] = amount`.
3. A relayer delivers the corresponding `RedeemEscrow` (or `RefundEscrow`) POST request; `onAccept` calls `withdraw(body, ...)`.
4. Inside `withdraw`, `token.call(...transfer...)` returns `success = true` (call didn't revert) but the encoded return data is `false` — no tokens are moved to `beneficiary`.
5. `withdraw` proceeds to decrement `_orders[commitment][token]`, delete the fee entry, set `_filled[commitment] = beneficiary`, and emit `EscrowReleased`. The escrowed tokens remain stuck in the `IntentGatewayV2` contract, unrecoverable by the beneficiary, since the order is now marked filled.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L674-676)
```text
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L706-710)
```text
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L720-722)
```text
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
