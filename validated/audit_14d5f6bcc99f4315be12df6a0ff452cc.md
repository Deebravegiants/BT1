## Analysis

The reachable analog is the Tron-target `IntentGatewayV2` deployment. Unlike the mainline EVM contracts, which route ERC-20 transfers through OpenZeppelin's `SafeERC20` (`safeTransferFrom`/`safeTransfer`, confirmed in `evm/src/apps/IntentGatewayV2.sol` and `evm/src/apps/intentsv2/IntentsBase.sol`), the Tron variant performs raw low-level calls and only checks that the call did not revert — it never decodes and validates the boolean return value from `transfer()`. [1](#0-0) 

This is the mirror-image of the code-423n4 H-09 bug class: instead of a non-compliant token (no return data) causing a false revert, a *compliant* token that returns `false` on a failed transfer (rather than reverting) is silently treated as a successful transfer, because `success` from the low-level `.call()` only reflects that the callee didn't revert — it says nothing about the decoded `bool` result.

### Root cause
`withdraw()` (escrow redemption/refund path) and the `SweepDust` branch of `onAccept()` both do:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [2](#0-1) 

and the same pattern for `SweepDust`: [3](#0-2) 

and for the tx-fee release: [4](#0-3) 

No `returndatasize()`/`abi.decode(data, (bool))` check is performed. Immediately after this "successful" transfer, the escrow accounting is unconditionally decremented (`_orders[body.commitment][token] -= amount;`) and `EscrowReleased`/`EscrowRefunded`/`DustSwept` events fire, marking the withdrawal as fulfilled regardless of whether the token actually moved funds.

### Why this is reachable and impactful
`withdraw()` is invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` requests — these are ISMP POST requests dispatched cross-chain and delivered by any relayer once fill/refund resolution occurs on the counterpart gateway; a relayer or the intent solver's own dispatched proof is the trigger, not a privileged admin action.

If the destination-side ERC-20 token is one whose `transfer()` returns `false` on failure without reverting (e.g., due to a paused state, blacklist check, or insufficient balance corner case reintroduced by upgrade), the gateway will:
1. Mark the escrow entry as spent (`_orders[...] -= amount`).
2. Emit `EscrowReleased`/`EscrowRefunded`.
3. Never actually deliver the tokens to `beneficiary`.

The result is a permanent loss of the escrowed funds for the intended recipient — the tokens remain stuck in the `IntentGatewayV2` contract with no accounting entry left to reclaim them, since `_orders[body.commitment][token]` has already been decremented to zero.

## Title
Unchecked ERC-20 boolean return value in `IntentGatewayV2` (Tron) escrow withdrawal/refund/dust-sweep leads to permanent loss of funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()` and the `SweepDust` handler in the Tron-targeted `IntentGatewayV2` use a raw low-level `.call()` to invoke `IERC20.transfer()` and only check that the call did not revert, never validating the ABI-decoded boolean return value. Tokens that return `false` on failure instead of reverting will cause the contract to mark escrowed funds as released/refunded/swept and delete the internal accounting, while the tokens never actually leave the contract.

### Finding Description
`_orders[body.commitment][token] -= amount;` executes unconditionally after the `.call()` succeeds (i.e., does not revert), regardless of the decoded return value. [5](#0-4) 
This is inconsistent with the main EVM deployment, which consistently wraps outgoing ERC-20 movement in OpenZeppelin's `SafeERC20`, which explicitly checks the decoded return value and reverts if it is `false`. [6](#0-5) 

### Impact Explanation
Permanent freezing/loss of user funds: once escrow accounting is zeroed and the corresponding event fired, there is no remaining code path to re-attempt the transfer or recover the tokens, even though the tokens physically remain locked in the gateway contract. This affects both order settlement (`RedeemEscrow`/`RefundEscrow`) and the `SweepDust`/transaction-fee-release paths, meeting the "permanent freezing of funds" criterion.

### Likelihood Explanation
Triggered by any properly-authenticated cross-chain `RedeemEscrow`/`RefundEscrow`/`SweepDust` message being delivered by a relayer once the fill/refund decision is made on the source side — no privileged actor is required. It depends on the destination-side token contract returning `false` rather than reverting on failure, a real-world (if less common) ERC-20 behavior (e.g., some legacy or custom tokens), making it a plausible, non-privileged trigger path for value loss.

### Recommendation
Replace the manual `token.call(...)` + `success`-only check with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the pattern already used in `evm/src/apps/IntentGatewayV2.sol` and `IntentsBase.sol`, so that both revert-on-failure and false-return failure modes are handled uniformly and safely before mutating escrow state.

### Proof of Concept
1. Configure (or have Hyperbridge governance list) a destination token whose `transfer()` implementation returns `false` on failure instead of reverting (e.g., due to a pausable/blacklist guard).
2. A user creates an intent order with that token as an input; a solver fills it and the settlement flow dispatches a `RedeemEscrow` request that is delivered to the Tron-side `IntentGatewayV2`.
3. If the token transfer internally fails (returns `false`) at delivery time — e.g., beneficiary is blacklisted or contract is paused momentarily — `withdraw()` still decrements `_orders[...]` to zero and emits `EscrowReleased`, permanently discarding the ability to reclaim the tokens, which remain stranded in the gateway contract. [7](#0-6)

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

**File:** evm/src/apps/IntentGatewayV2.sol (L26-27)
```text
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```
