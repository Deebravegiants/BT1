## Title
Escrow release/refund silently succeeds on failed TRC20 `transfer()` due to unchecked return-data in `IntentGatewayV2.withdraw()` — (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed order funds using a raw low-level `.call()` to the token's `transfer()` selector, but only checks that the *call itself* did not revert (`success`). It never decodes and validates the ABI-encoded `bool` return value that `transfer()` is supposed to return. Because many TRC20/non-standard ERC20 tokens return `false` on failure instead of reverting, a failed transfer can be mistaken for a successful one, causing escrow accounting to be finalized and permanently zeroed while the intended beneficiary never actually receives the tokens.

### Finding Description
`withdraw()` — reached from `onAccept()` for `RedeemEscrow`/`RefundEscrow` requests and from `onGetResponse()` after a cancel-from-source GET response — releases escrowed input tokens and fees to a beneficiary: [1](#0-0) 

For every non-native token, the release is performed as:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
This only verifies that the external call did not revert. It does not `abi.decode` the returned `bytes` as a `bool` (the pattern OpenZeppelin's `SafeERC20.safeTransfer` uses internally) to confirm the token actually reports success. Non-standard ERC20/TRC20 tokens (including some popular TRON tokens) commonly return `false` on failed transfers (e.g., due to a paused state, blacklist, or insufficient contract balance) rather than reverting. In that case `success` is `true` even though no tokens moved.

Immediately after this unguarded transfer, the escrow accounting is unconditionally decremented and the order is marked filled/refunded:
```solidity
_orders[body.commitment][token] -= amount;
...
_filled[body.commitment] = beneficiary;
```
The exact same unchecked pattern is repeated for the transaction-fee payout and for `SweepDust`: [2](#0-1) 

Note the contract already imports and uses `SafeERC20` (`using SafeERC20 for IERC20;`) elsewhere in the escrow-deposit path (`placeOrder`/`fillOrder` use `safeTransferFrom`), so the safe-transfer utility is available but was not used for outbound token releases in this file — unlike the EVM counterpart (`evm/src/apps/intentsv2/IntentsBase.sol`), which consistently uses `IERC20(token).safeTransfer(...)` for the same `_withdraw` logic: [3](#0-2) 

### Impact Explanation
This is reachable via the standard, unprivileged Intent Gateway settlement flow: any relayer can deliver a `RedeemEscrow`/`RefundEscrow` POST request (once dispatched by Hyperbridge) or a `GET` response used for source-side cancellation, both of which invoke `withdraw()`. If the escrowed token silently returns `false` on transfer instead of reverting, the protocol:
1. Permanently deletes/decrements the escrow accounting (`_orders[...] -= amount`), and
2. Marks the order as filled/refunded (`_filled[commitment] = beneficiary`), which blocks any retry or alternative recovery path,

while the solver or user beneficiary receives zero tokens. This is a direct, permanent loss of escrowed user/solver funds with no recovery mechanism (the same commitment cannot be withdrawn again since `_filled` is now set and/or the internal per-token order balance is already reduced to zero/incorrect state). This satisfies "concrete theft or permanent freezing of funds" for an unprivileged relayer/solver-reachable path.

### Likelihood Explanation
Likelihood is Medium-High specifically on Tron/TRC20 deployments, since TRON's ecosystem token implementations (including some widely used stablecoins historically) are known to deviate from strict ERC20 semantics and can return `false` instead of reverting under certain conditions (e.g., paused, blacklisted, insufficient balance edge cases due to fee-on-transfer or governance pausing). Any listed intent input/output token exhibiting this behavior, even transiently (e.g., temporarily paused by its own admin, or blacklist added mid-flight), would trigger silent fund loss the next time `withdraw()`/`SweepDust` executes for that token.

### Recommendation
Replace all raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` invocations in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer` (already imported via `using SafeERC20 for IERC20;`), which reverts on both call failure and a returned `false`, matching the pattern already used correctly in `placeOrder`/`fillOrder` and in the EVM sibling contract `IntentsBase.sol`.

### Proof of Concept
1. Register/allow a TRC20 token for intents whose `transfer()` implementation returns `false` (rather than reverting) when, e.g., the recipient is blacklisted or the contract is paused (a real, previously-observed TRC20 behavior).
2. A user places a cross-chain order escrowing this token via `placeOrder`; a solver fills it on the destination chain, and Hyperbridge dispatches a `RedeemEscrow` request back to the Tron source chain.
3. Before delivery, the token temporarily enters a state where `transfer()` returns `false` for the beneficiary (e.g., recipient briefly blacklisted, or contract briefly paused) without reverting.
4. Any relayer delivers the message; `onAccept` → `withdraw()` executes `token.call(...)`, which returns `success = true` (the call did not revert) even though the encoded boolean payload is `false` and no tokens were moved.
5. `_orders[commitment][token]` is decremented to zero and `_filled[commitment]` is set, permanently closing the order. The beneficiary never receives the escrowed tokens and has no path to reclaim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-683)
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
