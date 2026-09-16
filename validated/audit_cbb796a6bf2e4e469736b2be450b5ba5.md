### Title
Silent loss of escrowed intent funds via unchecked ERC20 `transfer` return-data in `IntentGatewayV2.withdraw`/`SweepDust` (Tron) - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed intent tokens (input tokens, fees, and dust) to solvers/beneficiaries using a raw low-level `.call` to the ERC20 `transfer` selector and only checks that the *call itself* did not revert (`success`), without decoding/validating the boolean payload the ERC20 standard returns. This is the same bug class as the referenced Fei report (`IWETH.transfer` return value unchecked in `EthUniswapPCVController`): a token that returns `false` on failure instead of reverting will make `success == true` even though no tokens were actually moved, causing the contract's internal escrow accounting to be decremented while the beneficiary/solver receives nothing.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the escrow-release path (`withdraw`) and the dust-sweep path (`SweepDust` handling) both perform ERC20 payouts like this:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) 

The same pattern is repeated for the tx-fee redemption: [2](#0-1) 

and for the `SweepDust` request kind: [3](#0-2) 

Note that the contract already imports `SafeERC20` and uses `safeTransferFrom`/`safeTransfer` correctly for *inbound* transfers when placing orders [4](#0-3) , but the *outbound* escrow-release/dust-sweep paths bypass `SafeERC20` and only check `success` from the raw `call`, never inspecting the returned `bool` payload. Per the ERC20 standard (and OpenZeppelin's own rationale for `SafeERC20`), a call can return `success == true` while the ABI-encoded return data is `false`, or a non-standard/malicious token can simply return `false` on failure without reverting (e.g., insufficient balance handled via a boolean return instead of a revert). In that scenario, the low-level call succeeds, `success` is `true`, and the code proceeds to decrement `_orders[body.commitment][token]` (or clear the fee/dust entry) as if the payout succeeded, even though the beneficiary received nothing.

Regardless of whether `success` is properly evaluated, the escrow accounting (`_orders[...] -= amount`) is unconditionally executed based on the call's revert status alone, not on verified token receipt. This is precisely the class of bug the Fei report flags: relying on an unchecked/partially-checked ERC20 return value for a token movement rather than a robust `safeTransfer`/return-data-checked call.

`withdraw()` is reached from `onAccept` (relayed `RedeemEscrow`/`CancelEscrow` settlement messages delivered by any relayer submitting a valid ISMP proof) and from `onGetResponse` (relayed GET-response proofs for cancellations), both of which are triggered by unprivileged relayers submitting proofs for cross-chain intent settlement — squarely within the in-scope "intents escrow" and "relayer... proof delivery" surface.

### Impact Explanation
If the underlying ERC20 (or a malicious/adversarial token registered as an intent input/output asset) returns `false` on a failed `transfer` instead of reverting, the escrow ledger (`_orders[commitment][token]`) is silently decremented to zero (or the appropriate amount) without the beneficiary/solver ever receiving the tokens. This results in **permanent freezing/loss of escrowed user or solver funds**: the order is marked filled/refunded, the corresponding `EscrowReleased`/`EscrowRefunded` event fires, and the tokens can never be reclaimed since the escrow record has already been zeroed out. This is a direct fund-loss vector matching the "concrete theft or permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Exploitability depends on the intent's input/output token being one that returns `false` rather than reverting on transfer failure (a known, if not universal, ERC20 implementation pattern), or on any transient failure condition of a standard token that returns false instead of reverting. Because the `IntentGatewayV2` contract in general (per its architecture) allows arbitrary ERC20 tokens to be used as intent inputs/outputs — it is not restricted to a vetted allowlist of "safe" tokens — an attacker or a user routing an order through a non-standard/adversarial token can trigger this condition deterministically. Likelihood is therefore Medium: it requires a specific token behavior, but such tokens are known to exist and the gateway does not restrict token choice.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check pattern in `withdraw()`, the fee-redemption block, and the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer`, which decodes and validates the return data (or requires no data, per EIP-20 non-standard tokens) and reverts on failure. This mirrors the report's exact recommendation ("add a require-statement or use `safeTransfer`") and is consistent with the `safeTransferFrom` usage already present elsewhere in the same file.

### Proof of Concept
1. Deploy a malicious/non-standard ERC20 token whose `transfer(address,uint256)` function returns `false` (ABI-encoded boolean) on failure instead of reverting (e.g., when a bridge governance flag disables outbound transfers, or on any internal require that's replaced with a boolean check).
2. Place a same-chain or cross-chain intent order using this token as an input asset via `IntentGatewayV2.placeOrder`, escrowing tokens into `_orders[commitment][token]`.
3. Have a solver fill the order (or invoke cancellation), causing `withdraw()` to be invoked via `onAccept`/`onGetResponse` after a relayer submits a valid settlement/timeout proof.
4. Configure/trigger the malicious token to return `false` (without reverting) for the specific `transfer` call inside `withdraw()`.
5. Because `success` is `true` (the call itself didn't revert), the code does not revert; `_orders[body.commitment][token] -= amount` executes and `EscrowReleased`/`EscrowRefunded` is emitted — while the beneficiary's token balance never increased. The escrowed funds are now unrecoverable, since the internal accounting shows the order as fully settled.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-722)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
