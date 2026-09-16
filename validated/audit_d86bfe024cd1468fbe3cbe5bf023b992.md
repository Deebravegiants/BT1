## Title
`IntentGatewayV2.withdraw()` (Tron) checks only the raw call `success` and ignores the ERC20 `transfer` return value, permanently freezing solver/user funds for non-compliant tokens - (`evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` abandons `SafeERC20.safeTransfer` for its escrow payout path and instead issues a raw low-level `.call()` with the `IERC20.transfer` selector, checking only that the call itself did not revert. It never inspects the ABI-encoded `bool` returned by the token. For any ERC20/TRC20 token that signals failure by returning `false` instead of reverting (a widely-used pattern on Tron, and explicitly the exact bug class flagged in the referenced report), the contract will treat a failed transfer as successful.

### Finding Description
`withdraw()` is the internal function invoked from `onAccept()` when a `RedeemEscrow` or `RefundEscrow` message is delivered from Hyperbridge (i.e. from any relayed cross-chain proof, an unprivileged/permissionless action): [1](#0-0) 

```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    _filled[body.commitment] = beneficiary;
    ...
    if (token == address(0)) {
        (bool sent,) = beneficiary.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
    } else {
        (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
        if (!success) revert TransferFailed();
    }

    _orders[body.commitment][token] -= amount;
    ...
```

`success` here only reflects whether the low-level call reverted, not whether the token's `transfer()` returned `true`. A non-standard token that returns `false` on failure (rather than reverting) makes `success == true` even though no tokens moved. The function then unconditionally decrements `_orders[body.commitment][token]` and (earlier, unconditionally) sets `_filled[body.commitment] = beneficiary`, finalizing the order as filled.

The same unchecked-return pattern recurs in the fee payout branch of `withdraw()`: [2](#0-1) 

and in the governance-triggered dust sweep inside `onAccept()`: [3](#0-2) 

Notably, `SafeERC20` is imported and used correctly (`using SafeERC20 for IERC20;`) everywhere else in this same contract (e.g. `safeTransferFrom` in `placeOrder`), and the EVM-native counterpart `IntentsBase.sol`/`IntentGatewayV2.sol` uses `IERC20(token).safeTransfer(beneficiary, amount)` in the equivalent function. The Tron fork specifically regressed this to a raw `.call()` without decoding the boolean return, reproducing exactly the vulnerability class described in the referenced Gitcoin `RoundImplementation.setReadyForPayout` report (unchecked ERC20 return value assumed successful).

### Impact Explanation
Once `withdraw()` runs, `_filled[body.commitment]` is set and the escrow ledger entry `_orders[body.commitment][token]` is decremented regardless of whether the token transfer actually succeeded. There is no retry path once the order is marked filled/refunded. If the output/input token used in an order is one that returns `false` instead of reverting on failure (blacklisted recipient, paused token, insufficient allowance/approval edge cases in custom TRC20 implementations, etc.), the beneficiary's tokens remain stuck in the `IntentGatewayV2` contract forever — a permanent loss of user/solver funds — while on-chain state records the order as already settled. This meets the "permanent freezing of funds" / concrete-loss bar.

### Likelihood Explanation
This is triggered purely by the normal, permissionless cross-chain settlement flow: any solver fills an order, and the resulting `RedeemEscrow`/`RefundEscrow` message is delivered via a relayed Hyperbridge proof to `onAccept`, which anyone can submit once a valid proof exists. No malicious admin/governance action is required — only that one of the escrowed tokens is a non-standard ERC20/TRC20 that returns `false` rather than reverting on a failed transfer, which is common in the Tron ecosystem this contract specifically targets.

### Recommendation
Replace the raw `.call()` + `success`-only check with `SafeERC20.safeTransfer`/`safeTransferFrom` (already imported and used elsewhere in this file), or manually decode and require the returned boolean:
```solidity
IERC20(token).safeTransfer(beneficiary, amount);
```
Apply the same fix to the fee-token payout in `withdraw()` and to the token branch of the `SweepDust` handler in `onAccept()`.

### Proof of Concept
1. Register/escrow an order whose input or fee token is a TRC20 contract that returns `false` on `transfer()` failure instead of reverting (e.g., recipient is blacklisted by the token, or token has a "paused" state that silently no-ops transfers and returns `false`).
2. Solver fills the order on the destination chain and triggers the `RedeemEscrow` message back to the source `IntentGatewayV2`.
3. A relayer delivers the proof; `onAccept` → `withdraw()` executes. The token's `transfer(beneficiary, amount)` call returns `false` but does not revert, so `success == true`.
4. `_filled[commitment]` is set and `_orders[commitment][token]` is decremented as if the payout succeeded, while `beneficiary` received nothing.
5. Tokens remain trapped in the `IntentGatewayV2` contract with no way for the beneficiary to reclaim them, since the order is already marked filled.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-682)
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
