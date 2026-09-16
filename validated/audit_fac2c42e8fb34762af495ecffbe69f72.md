## Analog Found

### Title
Unchecked ERC20/TRC20 transfer return value in Tron IntentGatewayV2 `withdraw()` can silently fail while escrow accounting still zeroes out - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed order funds and protocol fees using a raw low-level `.call()` encoding `IERC20.transfer.selector`, checking only that the call did not revert (`success`), but never decoding/validating the boolean return value the ERC20/TRC20 standard uses to signal transfer failure. This is the exact bug class from the reported analog (`FeeBuyback` not using `safeTransferFrom`/checking return data), applied to the intents escrow release path instead of a fee buyback.

### Finding Description
In `withdraw()`, escrowed input tokens and transaction fees are released to the beneficiary via: [1](#0-0) 

and dust is swept the same way: [2](#0-1) 

Both sites do `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check the outer `success` flag (i.e., that the call did not revert). They never inspect `returndata` to confirm the token actually returned `true`. Many ERC20/TRC20 tokens (non-reverting, "return false on failure" style tokens — which are common on Tron, e.g. tokens following the older TRC20 conventions) will return `abi.encode(false)` on a failed transfer instead of reverting. In that case `success == true` even though no tokens moved.

Crucially, right after this unchecked transfer, the escrow bookkeeping is unconditionally decremented as though the transfer succeeded: [3](#0-2) 

and the fee escrow slot is deleted regardless of whether the transfer actually delivered funds: [4](#0-3) 

This contrasts with the main EVM `IntentGatewayV2`/`IntentsBase`/`ExtrinsicIntents` flows in this repo, which consistently use `SafeERC20.safeTransferFrom`/`safeTransfer` for token movement (e.g. `IERC20(token).safeTransferFrom(msg.sender, ..., amount)` in `evm/src/apps/IntentGatewayV2.sol` and `evm/src/apps/intentsv2/ExtrinsicIntents.sol`), confirming that the Tron contract is the one that regressed to unchecked raw calls. [5](#0-4) [6](#0-5) 

`withdraw()` is invoked from the cross-chain/GET-response paths (`onGetResponse`) reachable by any relayer delivering a proven message, and from order-fill/refund flows reachable by any solver/user — none of these require privileged roles. [7](#0-6) 

### Impact Explanation
If the escrowed input token or fee token silently fails on transfer (returns `false` without reverting), the beneficiary receives nothing, but the contract still decrements `_orders[commitment][token]` and deletes the fee escrow entry as if the payout succeeded. The escrowed tokens remain locked in the contract with no accounting pointing to them, and the intended recipient permanently loses their entitled funds — a permanent freezing/loss of user/solver funds via a single relayed message delivery, matching the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
Reachable by any relayer/solver completing a normal order lifecycle (fill → redeem escrow, or cancel → refund escrow) — no privileged role is needed to trigger `withdraw()`. It requires the underlying token to be a non-reverting, return-false-on-failure ERC20/TRC20 (common enough in the Tron ecosystem this contract explicitly targets, e.g. paused, blacklisted, or insufficient-allowance/balance edge cases on some token implementations), and the operators/governance to have registered/allowed such a token as an input or fee token.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and `sweepDust`-equivalent code with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the rest of the codebase (`evm/src/apps/*`), so that both call failure and a `false` boolean return revert the transaction before escrow state is mutated.

### Proof of Concept
1. Operator configures an order whose input/fee token is a non-standard ERC20/TRC20 that returns `false` on failed transfer instead of reverting (e.g. due to an internal pause, blacklist, or insufficient contract balance edge case).
2. User places an order and escrows funds via `IntentGatewayV2.placeOrder`; solver fills it, triggering the redeem-escrow cross-chain message.
3. Relayer delivers the proof and `onGetResponse`/`onAccept` calls `withdraw(body, false)`.
4. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `(true, abi.encode(false))` — `success` is `true` so `if (!success) revert TransferFailed();` does not trigger.
5. `_orders[body.commitment][token] -= amount;` executes, zeroing the escrow record, while `beneficiary` received zero tokens — funds are permanently stranded in the contract with no remaining accounting reference to reclaim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-683)
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
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-723)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L732-744)
```text
    /**
     * @notice Handles the response for a previously dispatched storage query (GET request).
     * @dev This function is called by the host to process the response of a GET request.
     * @param incoming The response data structure for the GET request.
     * Only the host can call this function.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
}
```

**File:** evm/src/apps/IntentGatewayV2.sol (L249-251)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L191-196)
```text
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
```
