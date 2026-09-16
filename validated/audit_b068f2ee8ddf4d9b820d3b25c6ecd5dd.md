### Title
Unchecked low-level `.call` return value for ERC20 transfers can silently fail while escrow accounting is updated, permanently locking funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.withdraw()` and the `SweepDust` branch of `onAccept()` release escrowed ERC20 tokens using a raw low-level `.call` with the `IERC20.transfer.selector`, and only check the outer `success` boolean of the call itself — they never decode/verify the ABI-encoded `bool` return value that ERC20 `transfer()` implementations are expected to return. This is the same class of unsafe-transfer bug flagged in the external report (using `transfer()`/raw call instead of `safeTransfer()`), but is actually worse here because failures are silently swallowed rather than reverting, while internal escrow accounting is unconditionally decremented.

### Finding Description
In `withdraw()`, escrowed tokens are released like this: [1](#0-0) 

and the transaction-fee payout: [2](#0-1) 

The same unsafe pattern is used for dust sweeping, triggered by a `SweepDust` message from Hyperbridge: [3](#0-2) 

Contrast this with the rest of the same file (and the equivalent EVM `IntentGatewayV2.sol`), which correctly uses `SafeERC20.safeTransferFrom`/`safeTransfer` for pulling and refunding assets, e.g. `IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount)`: [4](#0-3) 

`SafeERC20` is even imported and aliased (`using SafeERC20 for IERC20;`) in this very contract: [5](#0-4) 

but the `withdraw()`/`SweepDust` payout paths bypass it and instead check only `(bool success,) = token.call(...)`. For any ERC20 token that returns `false` on failure instead of reverting (e.g. tokens following the strict `bool`-returning EIP-20 spec without reverting on insufficient balance/blacklist/paused state), `token.call(...)` itself will still return `success == true` (the call didn't revert), even though the encoded return data is `false` and no tokens were actually moved. Because the code never inspects `returndata`, this failure path is invisible to the contract.

### Impact Explanation
In `withdraw()`, once the (silently failed) transfer branch is executed, the code unconditionally proceeds to decrement escrow accounting: `_orders[body.commitment][token] -= amount;` (line 710), and for fees, `delete _orders[body.commitment][TRANSACTION_FEES];` (line 722), and finally marks the order as filled/refunded (`_filled[body.commitment] = beneficiary;`, line 693) and emits `EscrowReleased`/`EscrowRefunded`. Because `withdraw()` is only reachable via the `RedeemEscrow`/`RefundEscrow` message path in `onAccept()` (see line 634), this whole flow executes exactly once per commitment (authenticated Hyperbridge message). If the underlying transfer silently fails, the beneficiary never receives their tokens, but the escrow bookkeeping is already zeroed out and the order is marked filled — the tokens become permanently locked/unrecoverable inside the `IntentGatewayV2` contract with no remaining code path to re-attempt distribution to the rightful beneficiary. This is a direct permanent freezing-of-funds condition for solvers/users whose intents were escrowed with a non-reverting ERC20.

### Likelihood Explanation
Reachability requires only that one of the tokens used in an intent/order is a "false-returning" ERC20 (a known and common pattern among real-world tokens), and that the transfer legitimately or maliciously fails at redemption time (e.g., beneficiary temporarily blacklisted, paused token, insufficient balance in `IntentGatewayV2` due to prior dust/fee accounting drift). No privileged role is needed — any relayer delivering a normal `RedeemEscrow`/`RefundEscrow`/`SweepDust` message triggers the vulnerable code path, and the failure mode is silent, so it is unlikely to be caught before funds are locked.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` (lines 706, 720) and in the `SweepDust` handling (line 674) with `SafeERC20.safeTransfer()`, consistent with the rest of the contract, so that both a reverting failure and a `false` boolean return are correctly treated as failures and revert the whole transaction instead of allowing escrow state to be finalized without the tokens actually moving.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with an ERC20 token whose `transfer()` returns `false` on failure instead of reverting (e.g., a token that returns `false` when the recipient is blacklisted or balance is momentarily insufficient due to a race).
2. A user escrows tokens via the normal order flow, populating `_orders[commitment][token]`.
3. Hyperbridge delivers a `RedeemEscrow` message; `onAccept()` calls `withdraw()`.
4. At line 706, `token.call(...)` executes; the token's `transfer()` returns `false` without reverting, so `success == true` from the low-level call's perspective.
5. Execution continues past the `if (!success) revert TransferFailed();` check, decrements `_orders[commitment][token]` (line 710), and marks the order filled (line 693), emitting `EscrowReleased`.
6. The beneficiary never received the tokens, and the accounting has already been zeroed, providing no future call path to retry the transfer — the tokens are permanently stuck in the contract.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L38-56)
```text
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import {ICallDispatcher, Call} from "../../../src/interfaces/ICallDispatcher.sol";


/**
 * @title IntentGatewayV2
 * @author Polytope Labs (hello@polytope.technology)
 *
 * Implements the IntentGatewayV2 contract for Tron
 *
 * @dev The IntentGateway allows for the creation and fulfillment of same-chain & cross-chain orders.
 */
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L717-722)
```text
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
