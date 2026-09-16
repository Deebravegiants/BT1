### Title
Unchecked ERC20 return value in `IntentGatewayV2.withdraw` and `SweepDust` handling causes silent transfer failures and permanent freezing of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.sol` uses a raw low-level `.call` with `IERC20.transfer.selector` to pay out escrowed order tokens and swept dust, but only checks the boolean `success` of the call itself and never inspects/decodes the ERC20 return data. This is the same class of bug flagged in the referenced report (insufficient handling of ERC20 tokens that don't revert on failure), but here it is even weaker than the pattern criticized in the report because the code doesn't even attempt `abi.decode(data, (bool))` — it accepts any call that doesn't revert as a successful transfer, regardless of what the token actually returned.

### Finding Description
In the `withdraw` function, which is reached from `onAccept` when a `RedeemEscrow`/`RefundEscrow` message is delivered from the paired-chain gateway via Hyperbridge, escrowed ERC20 tokens are released to the beneficiary using: [1](#0-0) 

```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;
```

Tokens like USDT (on some chains) or other ERC20 implementations that return `false` instead of reverting on a failed transfer (e.g., due to blacklist restrictions, paused state, or insufficient contract balance from prior fee-on-transfer/dust accounting drift) will make this `.call` return `success == true` even though no tokens moved. The code accepts this as success, decrements `_orders[body.commitment][token]` as if the transfer succeeded, and emits `EscrowReleased`/`EscrowRefunded`. The same unchecked pattern is used for the transaction fee payout in the same function: [2](#0-1) 

and for dust sweeping triggered by a Hyperbridge-only `SweepDust` message: [3](#0-2) 

This is reachable from a single relayed Hyperbridge message (`RedeemEscrow`/`RefundEscrow`/`SweepDust`), which is the standard, unprivileged path any solver/user order fill or refund takes through the intents flow — no admin/relayer/prover collusion required, only a token whose behavior differs from the standard revert-on-failure ERC20 semantics (or a state where the call target reverts data-less but `success` bit gets swallowed, e.g. proxy tokens, or non-standard low-level return handling on Tron specifically, which has known quirks around TRC20/`transfer` return handling).

By contrast, the primary EVM `IntentGatewayV2` implementation used elsewhere in the codebase (`sdk/packages/core/contracts/apps/IntentGatewayV2.sol` and its consumer `evm/src/apps/IntentGatewayV2.sol`) consistently uses OpenZeppelin's `SafeERC20.safeTransferFrom`/`safeTransfer` for token movements, e.g.: [4](#0-3) [5](#0-4) 

The Tron fork deviates from this safe pattern specifically in its `withdraw`/`SweepDust` code paths, importing `SafeERC20` ( [6](#0-5) ) but not actually using it for these payouts.

### Impact Explanation
If the escrowed token's `transfer` returns `false` without reverting (a known behavior for several tokens, and specifically a documented quirk of TRC20 tokens on Tron where `transfer` can return `false` on failure rather than reverting), the beneficiary silently receives nothing while the contract's internal accounting is updated as if the payout succeeded. This permanently freezes the beneficiary's fair funds in the intents escrow: their tokens (deposited on the source chain and marked as filled/refunded here) are lost with no way to retry, since `_orders[body.commitment][token]` is decremented and the corresponding withdrawal state is marked complete (`_filled[body.commitment] = beneficiary`). This matches "permanent freezing of funds" impact criteria.

### Likelihood Explanation
Likelihood is moderate-to-high for the Tron deployment: TRC20 tokens are known to sometimes deviate from strict ERC20 revert semantics, and this contract is explicitly built for Tron (`@title IntentGatewayV2 ... Implements the IntentGatewayV2 contract for Tron`, [7](#0-6) ). Any solver filling an order with such a token, or any refund/sweep flow, triggers this vulnerable code path with no privileged action required beyond normal intent settlement via Hyperbridge message delivery.

### Recommendation
Replace the raw `.call` + `success`-only check with `SafeERC20.safeTransfer` (already imported via `using SafeERC20 for IERC20;`) in `withdraw` (both the token payout loop and the fee payout) and in the `SweepDust` handling branch of `onAccept`, consistent with the pattern already used in `evm/src/apps/IntentGatewayV2.sol` and `ExtrinsicIntents.sol`.

### Proof of Concept
1. An order is created and filled/refunded such that `withdraw` is invoked via `onAccept` with `kind == RequestKind.RedeemEscrow` (or `RefundEscrow`), for a token `T` that returns `false` on a failed `transfer` call instead of reverting (representative of common TRC20 behavior on Tron, e.g. due to the contract being paused, the beneficiary being blacklisted, or insufficient balance from prior fee-on-transfer inconsistencies).
2. In `withdraw`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `success = true` (the low-level call executed) with return data encoding `false`.
3. The code only checks `if (!success) revert TransferFailed();`, which passes since `success == true`; the `false` return value is never decoded.
4. `_orders[body.commitment][token] -= amount;` executes, and `EscrowReleased`/`EscrowRefunded` is emitted, marking the withdrawal as complete despite the beneficiary receiving zero tokens.
5. The beneficiary's escrowed funds are now permanently unrecoverable — there is no other code path to re-trigger payout for that commitment/token pair.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L38-41)
```text
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L47-55)
```text
/**
 * @title IntentGatewayV2
 * @author Polytope Labs (hello@polytope.technology)
 *
 * Implements the IntentGatewayV2 contract for Tron
 *
 * @dev The IntentGateway allows for the creation and fulfillment of same-chain & cross-chain orders.
 */
contract IntentGatewayV2 is HyperApp, EIP712 {
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/apps/IntentGatewayV2.sol (L248-251)
```text
                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```
