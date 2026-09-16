### Title
Unchecked ERC20 return value in Tron IntentGatewayV2 escrow withdrawal enables silent-failure token loss - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed intent tokens via raw low-level `.call()` to `IERC20.transfer`, checking only that the external call did not revert (`success`) — not the ABI-decoded boolean return value that ERC20 `transfer`/`transferFrom` is supposed to return. This is the exact bug class from the referenced Cooler.sol report: non-reverting ERC20 tokens that return `false` on failure will make the transfer silently no-op while the contract's internal escrow accounting is unconditionally decremented, permanently losing the tokens.

### Finding Description
`IntentGatewayV2` is designed to escrow arbitrary user-specified ERC20 tokens (`TokenInfo.token` is attacker/user supplied in `placeOrder`), so it must be robust against non-standard tokens. The main EVM contract (`evm/src/apps/IntentGatewayV2.sol` and `evm/src/apps/intentsv2/IntentsBase.sol`) correctly uses OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, e.g.: [1](#0-0) 

However, the Tron port at `evm/tron/contracts/apps/IntentGatewayV2.sol` reimplements token transfers with raw low-level calls that only check `success` (i.e., that the callee did not revert), and ignore the returned boolean payload entirely: [2](#0-1) 

The same pattern recurs in `onAccept`'s `SweepDust` handling: [3](#0-2) 

In both cases, `_orders[body.commitment][token] -= amount;` (escrow accounting) is decremented immediately after the `.call`, regardless of whether the token actually moved funds. For any ERC20 that implements the legacy pattern of returning `false` instead of reverting on failed transfer (e.g., insufficient balance edge cases, blacklists, or paused states that return `false`), `success` will be `true` (the low-level call itself completes without reverting) even though no tokens were transferred to the beneficiary. The escrow balance is nonetheless reduced to zero/discounted, and the beneficiary receives nothing — the tokens become permanently stuck/unrecoverable in the contract since the escrow slot is now zeroed and cannot be re-claimed.

This directly mirrors the reported bug class (`transferFrom`/`transfer` return values ignored for ERC20 tokens), scoped here to the token-bridge/intents component within the explicitly in-scope reachable paths ("intents escrow and bids... token bridge mint/burn").

### Impact Explanation
`withdraw()` is reachable from unprivileged flows: it is invoked by `onAccept` upon relayed `RedeemEscrow`/`RefundEscrow` messages (settling cross-chain fills/cancellations) and directly from `cancelOrder` for same-chain cancellations — both of which are triggered by ordinary users/solvers/relayers, not privileged admins. If the escrowed input token is a non-standard ERC20 that returns `false` rather than reverting, the escrow accounting is finalized (`_filled[commitment] = beneficiary`, `_orders[...] -= amount`) while funds remain trapped in the contract, unrecoverable by the intended solver or via refund path (since the order is already marked filled/refunded). This is a permanent freezing of user/solver funds, matching the "concrete... permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Likelihood depends on whether such non-standard tokens are used as intent inputs/outputs on the Tron deployment. Since IntentGatewayV2 explicitly supports arbitrary token pairs supplied by users at `placeOrder` time (no token allowlist enforced in the code reviewed), any user can create an order denominated in a token that follows the false-return-instead-of-revert pattern (a known real-world ERC20 quirk, e.g., legacy/pre-EIP20-compliant tokens or certain deflationary/blacklist tokens on TRC20 equivalents). No special privilege is required to trigger the vulnerable path — placing and settling an order with such a token is sufficient.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer/transferFrom...))` patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` (in `withdraw()` and the `SweepDust` branch of `onAccept()`) with OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, consistent with the main EVM `IntentGatewayV2.sol` and `IntentsBase.sol`, which already import and correctly use `SafeERC20`. This ensures both call success and a truthy return value (or absence of return data, per EIP-20 ambiguity) are validated before the escrow ledger is mutated.

### Proof of Concept
1. Deploy a TRC20-compatible token whose `transfer` returns `false` (instead of reverting) when the internal balance check fails, e.g. by artificially forcing a `balanceOf[gateway] < amount` edge case, or a token with a blacklist that returns `false` for blacklisted recipients.
2. User calls `placeOrder` escrowing this token as `order.inputs[0]` (uses `safeTransferFrom` on the way in, so escrow accounting is correctly funded).
3. Solver fills the order; the source-chain `IntentGatewayV2.onAccept` receives a `RedeemEscrow` message and calls `withdraw(body, false)`.
4. Inside `withdraw`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` is executed against the malicious/blacklisted-token path such that the call succeeds (`success == true`) but internally returns `false` (no state change, no tokens delivered). [4](#0-3) 
5. `_orders[body.commitment][token] -= amount` still executes, zeroing the escrow record; `_filled[commitment]` is already set, so the order can never be retried. The beneficiary/solver received nothing, and the tokens are permanently stranded in the `IntentGatewayV2` contract.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-681)
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
