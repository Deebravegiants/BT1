## Analysis

`evm/tron/contracts/apps/IntentGatewayV2.sol` — the Tron fork of `IntentGatewayV2` — diverges from the canonical EVM implementation in `evm/src/apps/intentsv2/IntentsBase.sol`, which correctly uses `SafeERC20.safeTransfer`/`safeTransferFrom` (e.g. `IERC20(token).safeTransfer(beneficiary, amount)` [1](#0-0) ). The Tron variant instead uses a raw low-level `.call` with the `transfer` selector and only checks that the *call itself* did not revert, never inspecting the ABI-decoded boolean return value.

### Title
Escrow/fee/dust payouts in Tron `IntentGatewayV2.withdraw`/`onAccept` treat non-reverting `false`-returning ERC20 transfers as success, permanently freezing escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()` and the `SweepDust` branch of `onAccept()` pay out ERC20 tokens (escrowed order funds, transaction fees, and swept dust) using a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only revert `if (!success)`, where `success` merely reflects whether the external call reverted — not whether the token's `transfer` actually returned `true`.

### Finding Description
In `withdraw()`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
...
_orders[body.commitment][token] -= amount;
``` [2](#0-1) 

and identically for fee redemption:
```solidity
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
delete _orders[body.commitment][TRANSACTION_FEES];
``` [3](#0-2) 

and for `SweepDust` handling in `onAccept()`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [4](#0-3) 

For any ERC20/TRC20 token that follows the non-reverting pattern (returns `false` instead of reverting on failed transfer — a widespread pattern on Tron/TRC20 tokens and several EVM tokens), the low-level `.call` reports `success == true` (the call executed without reverting) even though no tokens moved because `transfer` returned `false`. The code never decodes/checks the returned boolean.

Consequently:
- In `withdraw()`, `_orders[body.commitment][token] -= amount` is decremented and `_filled[body.commitment] = beneficiary` is set even though the beneficiary received nothing — the escrow accounting is silently wiped out for funds that were never actually paid, permanently freezing them (no other code path re-credits `_orders`).
- In the `SweepDust` branch, `DustSwept` is emitted and the loop proceeds as if funds were transferred, when they were not, again permanently losing the swept dust.

This is functionally identical to the reported bug class (`transfer`/`transferFrom` used without checking the boolean return value, unlike `safeTransfer`/`safeTransferFrom`), except here the impact is compounded because the codebase author is clearly aware of the pattern elsewhere (`IntentsBase.sol` uses `SafeERC20`), making this specific Tron duplication a regression that silently drops the return-value check.

### Impact Explanation
This causes concrete permanent loss/freezing of escrowed order funds and fees: the internal escrow ledger (`_orders`) is decremented and the order is marked `_filled` as if beneficiaries were paid, while the tokens remain permanently stuck in the `IntentGatewayV2` contract with no accounting path left to recover them for the affected beneficiaries. This satisfies the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
`withdraw()` is reached via `onAccept` for `RedeemEscrow`/`RefundEscrow` requests dispatched cross-chain and delivered by any relayer with a valid ISMP proof [5](#0-4) , and also via `onGetResponse` for GET-based refund flows [6](#0-5)  — both reachable by a normal solver/relayer submitting a delivery, not requiring any privileged role. The trigger condition (a token whose `transfer` returns `false` rather than reverting) is a known, common token behavior class, especially relevant on the Tron/TRC20 ecosystem this contract specifically targets.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` payout patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` with OpenZeppelin's `SafeERC20.safeTransfer` (the library is already imported and used via `safeTransferFrom` elsewhere in the same file [7](#0-6) ), consistent with `IntentsBase.sol`'s `_withdraw` implementation [8](#0-7) .

### Proof of Concept
1. An order escrows a TRC20/ERC20 token whose `transfer()` returns `false` on failure instead of reverting (e.g., insufficient allowance/balance edge cases, blacklist checks, or paused-transfer tokens common on Tron).
2. A relayer delivers a valid `RedeemEscrow`/`RefundEscrow` post request (or GET response) triggering `withdraw()`.
3. The token's `transfer` call executes without reverting but returns `false` (e.g., beneficiary is blacklisted, or contract balance momentarily manipulated by a reentered flow); `success` from the low-level `.call` is `true` since the call didn't revert.
4. `_orders[body.commitment][token] -= amount` executes and `_filled[body.commitment]` is set, marking the order as paid, while the beneficiary received zero tokens — the tokens remain locked in the contract permanently with no ledger entry left pointing to them.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L38-39)
```text
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```
