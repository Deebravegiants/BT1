### Title
Withdrawal of escrowed native ETH in IntentGatewayV2 / IntentsBase reverts entirely (no fallback path) when beneficiary cannot receive ETH, permanently freezing escrowed order funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`, `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
The Foundation report describes `_sendValueWithFallbackWithdraw`/`withdrawFor`, where a failed ETH push is captured in `pendingWithdrawals` but can only be redeemed to the very same (possibly non-payable) address, freezing funds. Hyperbridge's intents settlement contracts have an analogous but strictly worse pattern: when releasing escrowed native ETH to an order's `beneficiary`, a failed low-level call causes the whole withdrawal transaction to revert, with **no fallback escrow bookkeeping at all** and no alternate redemption path.

### Finding Description
In `IntentGatewayV2.withdraw`, escrowed native ETH is released directly to the `beneficiary` decoded from the `WithdrawalRequest`: [1](#0-0) 
If `token == address(0)` and the low-level `call` to `beneficiary` fails (e.g., beneficiary is a contract without a payable `receive`/`fallback`, or one that reverts, or exceeds any implicit gas stipend), the function reverts with `InsufficientNativeToken()` before the escrow is decremented. The equivalent EVM-mainline logic lives in `IntentsBase._withdraw`, which uses `_sendValue(beneficiary, amount)` for native transfers with the same all-or-nothing semantics: [2](#0-1) 

Unlike the Foundation bug (where a `pendingWithdrawals` fallback at least records the debt so it can eventually be claimed, and the Foundation team even improved it via a migration to FETH), the intents contracts here have **no recorded pending-withdrawal fallback whatsoever** for the native-ETH branch. The `beneficiary` field is fixed by the signed/committed order (`body.beneficiary`), and there is no `withdrawTo`, no escrow-to-token conversion, and no way for a filler/solver or the order originator to redirect settlement to a different, ETH-capable address. If `beneficiary` is a contract that cannot receive native value, the withdrawal call can never succeed, and the escrowed ETH for that commitment (`_orders[commitment][address(0)]`) remains locked in the contract indefinitely, with no owner/governance rescue function shown in the reachable withdraw path.

### Impact Explanation
This is a classic "permanent freezing of funds" bug in the intents escrow. Escrowed native ETH tied to a specific order commitment becomes unrecoverable if the beneficiary address (attacker-controlled input in some flows, or a solver/relayer address that later becomes a non-payable contract, e.g., after a proxy upgrade or a multisig change) cannot accept a plain ETH push. Because the withdrawal is the terminal state-transition for that order (`onGetResponse`/fill finalize path also marks `_filled[commitment] = beneficiary`, so retrying with a different beneficiary is not possible after that point in some flows), the funds can be trapped without any operator escape hatch visible in this code path. This qualifies as Medium/High severity freezing-of-funds under the same reasoning as the original Foundation report, and is arguably worse here because there's no escrow-to-alternate-asset fallback at all.

### Likelihood Explanation
Reachable by any unprivileged actor: any user/solver who creates or fills an intent order can specify (or be assigned via signature) a `beneficiary` address; if that address is (or later becomes) a contract with no payable fallback, every subsequent `withdraw`/`onGetResponse` call for that commitment's native-ETH leg reverts deterministically. No special privileges or timing are required to trigger the freeze — it happens naturally whenever a smart-contract beneficiary rejects value transfers.

### Recommendation
- Do not let a failed native transfer revert escrow release entirely. Mirror the pattern used elsewhere in the same codebase (e.g., `WrappedHyperFungibleToken.onAccept`/`onPostRequestTimeout`), which falls back to wrapping native ETH into the ERC-20 (WETH) form and delivering that instead when the `call` fails: [3](#0-2) 
- Alternatively, record a per-beneficiary pending-withdrawal balance (as Foundation's fix direction suggested) and expose a `withdrawTo`/pull-based redemption function, decoupling the fixed `beneficiary` field from the actual receiving address.
- Ensure escrow accounting (`_orders[commitment][token] -= amount`) and `_filled` marking never happen out of sync with a reverted transfer, and provide a governance/anyone-callable sweep/rescue mechanism for orders whose beneficiary can never accept the asset.

### Proof of Concept
1. Create/fill an intent order whose native-ETH `output`/refund beneficiary is set to a contract address with no `receive()`/payable `fallback()` (or one that always reverts on receiving ETH).
2. Trigger the withdrawal path (`withdraw(body, isRefund)` in `IntentGatewayV2.sol`, reached via `onAccept`/`onGetResponse`) once conditions for release/refund are met.
3. The low-level `call{value: amount}("")` to `beneficiary` fails; the function reverts with `InsufficientNativeToken()` at line 704 in `evm/tron/contracts/apps/IntentGatewayV2.sol`, and `_orders[commitment][address(0)]` is never decremented.
4. Because `beneficiary` is fixed to the order commitment and there is no fallback/pull-withdrawal mechanism, every future call to release this specific escrow leg reverts the same way — the escrowed ETH is permanently stuck in the contract. [4](#0-3) [5](#0-4)

### Citations

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-324)
```text
        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```
