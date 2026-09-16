## Finding

The Tron variant of `IntentGatewayV2` uses raw low-level `.call()` for ERC20 transfers and only checks that the call didn't revert (`success`), never decoding the returned boolean. This is the exact bug class from the report (`CollateralEscrowV1._withdrawCollateral` not checking transfer's boolean return), reachable through the intents escrow settlement path.

### Title
Unchecked ERC20 boolean return in `IntentGatewayV2.withdraw` permanently locks escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()`, invoked from `onAccept` when a relayed `RedeemEscrow`/`RefundEscrow` ISMP message arrives, releases escrowed tokens using a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only verifies that the low-level call itself succeeded, not that the token's return value was `true`.

### Finding Description
In `withdraw()`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
`success` is `true` whenever the callee doesn't revert, regardless of whether the ERC20 `transfer` actually moved tokens. Any ERC20 that follows the "return `false` on failure instead of reverting" convention (e.g. paused/blacklisted transfers, deflationary/fee tokens hitting an edge condition, or any non-standard implementation) will make this call succeed (`success == true`) while zero tokens are moved. [1](#0-0) 

Because the check passes, execution proceeds to decrement escrow accounting unconditionally:
```solidity
_orders[body.commitment][token] -= amount;
```
and `_filled[body.commitment] = beneficiary;` was already set at the top of `withdraw()` before the loop even runs. [2](#0-1) 

The same unchecked pattern recurs for the fee-token payout in the same function:
```solidity
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
``` [3](#0-2) 

and in the `SweepDust` handler inside `onAccept`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [4](#0-3) 

The reachable path is: a solver fills an order cross-chain → the destination gateway dispatches a `RedeemEscrow`/`RefundEscrow` ISMP POST → an (unprivileged) relayer delivers the proof to the source-chain `IntentGatewayV2.onAccept` → `authenticate()` only checks the message originates from the paired gateway instance, not anything about the token behavior → `withdraw()` executes the flawed transfer check. [5](#0-4) 

By contrast, the non-Tron EVM implementation of the same escrow logic (`IntentsBase._withdraw`) correctly uses `SafeERC20.safeTransfer`, which reverts on a `false` return:
```solidity
IERC20(token).safeTransfer(beneficiary, amount);
```
confirming the Tron file is the outlier lacking the safe-transfer guard. [6](#0-5) 

### Impact Explanation
Once `withdraw()` runs with a token that silently returns `false`, the contract marks the order `_filled`/refunded and decrements `_orders[commitment][token]` even though the beneficiary received nothing. Because the order is now considered settled, there is no remaining code path to re-claim the escrowed balance — the tokens remain stuck in the `IntentGatewayV2` contract while the escrow accounting shows them as already paid out. This is a permanent loss/freezing of user or solver funds, matching the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
Likelihood depends on the specific token used as escrow input/fee token exhibiting a non-reverting failure mode (pausable, blacklistable, or otherwise non-standard ERC20s are common in production token lists), and is triggered through the normal, unprivileged relayer-delivery path of intent settlement — no admin or governance action is required.

### Recommendation
Replace the raw `token.call(...)` + `success`-only check with `SafeERC20.safeTransfer`/`safeTransferFrom` (as already done in `evm/src/apps/intentsv2/IntentsBase.sol`), or explicitly decode and check the boolean return value in addition to `success`, for all three transfer sites in `evm/tron/contracts/apps/IntentGatewayV2.sol` (`withdraw`'s token loop, the fee payout, and the `SweepDust` handler).

### Proof of Concept
1. Deploy/escrow using an ERC20 that returns `false` instead of reverting on transfer failure (e.g. a token that pauses transfers to a specific address, or a mock returning `false` under a certain condition).
2. Place a cross-chain order with that token as input; a solver fills it on the destination chain, triggering a `RedeemEscrow` dispatch back to source.
3. A relayer delivers the message to `onAccept` → `withdraw()`; the token's `transfer` call returns `false` but doesn't revert, so `success == true`.
4. `_orders[commitment][token]` is decremented and `_filled[commitment]` is set, but `beneficiary`'s balance never increases — the escrowed tokens are permanently stranded in the gateway contract with no remaining code path to recover them.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
