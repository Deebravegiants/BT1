### Title
Missing ERC-20 return-value validation in `IntentGatewayV2.withdraw()`/`SweepDust` allows silent transfer failures to permanently freeze escrowed funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron deployment of `IntentGatewayV2` diverges from the canonical EVM implementation by using raw low-level `.call` for outbound token transfers in `withdraw()` and the `SweepDust` request handler, checking only that the call did not revert (`success`) but never validating the ERC-20/TRC-20 return value as required by the token standard. This is the exact bug class flagged in the external MetaMask report: a token that returns `false` on failure instead of reverting is silently treated as a successful transfer.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the `withdraw()` internal function transfers escrowed tokens to a beneficiary using: [1](#0-0) 
and settles the transaction fee escrow the same way: [2](#0-1) 
The `SweepDust` handler in `onAccept` uses the identical unsafe pattern to sweep protocol dust to a beneficiary: [3](#0-2) 

In every case, only the boolean `success` returned by the low-level `call` is checked; the returned `bytes` (which for ERC-20 `transfer` should decode to `true`) is never inspected. Per the ERC-20 standard, some conforming tokens return `false` on failure instead of reverting; such a call reports `success == true` here even though no tokens moved.

Critically, `withdraw()` unconditionally updates internal accounting *before/regardless of* whether the token transfer actually delivered funds: [4](#0-3) 
`_filled[body.commitment] = beneficiary` is set and `_orders[body.commitment][token] -= amount` is decremented as soon as the low-level call returns `success == true`, even if the token itself signaled failure via a `false` return value.

This directly matches the reported bug class ("no validation that the token transfer succeeded by returning `true`, as required by the ERC-20 standard... could result in silent failures... allowing tokens that don't revert on failures and just return `false` to be incorrectly treated as successfully transferred"), but here the affected code path is the actual custody/settlement logic of a cross-chain intents escrow, not just an enforcer hook.

Notably, the canonical (non-Tron) implementation in `evm/src/apps/intentsv2/IntentsBase.sol` avoids this entirely by using OpenZeppelin's `SafeERC20.safeTransfer`, which reverts on a `false` return: [5](#0-4) 
The Tron variant imports `SafeERC20` and uses it correctly for *inbound* escrow transfers (`safeTransferFrom` in `placeOrder`), but reverts to unchecked low-level calls for *outbound* withdrawal and dust-sweep transfers — an inconsistency that introduces the vulnerability only on the payout path.

### Impact Explanation
`withdraw()` is invoked from `onAccept()` (for `RedeemEscrow`/`RefundEscrow` requests delivered via a relayed ISMP message from Hyperbridge) and from `onGetResponse()` (for source-chain cancellations), both of which are triggered by an unprivileged relayer submitting a valid cross-chain proof/message — no special privilege is required to trigger the flawed code path. If the escrowed token is one that returns `false` on transfer failure (e.g., due to a paused/blacklisted state, an internal balance edge case, or purpose-built malicious/non-standard TRC-20 token registered as an input asset), the beneficiary receives no funds, yet:
- the escrow accounting is permanently decremented (`_orders[...] -= amount`), and
- the order is marked filled/finalized (`_filled[commitment] = beneficiary`),
making the escrowed funds **permanently unrecoverable** — neither the solver nor the original user can claim them again, since replay/refund paths check `_filled`/`_orders` state that has already been consumed. This satisfies the "permanent freezing of funds" impact bar for a token-bridge/intents-escrow settlement path.

### Likelihood Explanation
The Tron intents gateway can register arbitrary tokens as escrowed inputs and fee tokens (via governance-set params or per-order token addresses), so exposure depends on which TRC-20 tokens end up escrowed. Non-reverting-on-failure tokens are a well-documented class of ERC-20/TRC-20 tokens in production; combined with the low-privilege trigger (any relayer delivering a valid but token-transfer-failing settlement), likelihood is realistic in a live deployment, though it is contingent on such a token being in use as an input or fee token on the Tron deployment.

### Recommendation
Replace all outbound low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` (`withdraw()` and the `SweepDust` branch of `onAccept()`) with OpenZeppelin's `SafeERC20.safeTransfer`, matching the pattern already used for inbound transfers in the same file and for both directions in `evm/src/apps/intentsv2/IntentsBase.sol`. This ensures transfers that return `false` instead of reverting cause the whole settlement transaction to revert, preserving escrow accounting until a genuinely successful transfer occurs.

### Proof of Concept
1. Governance/owner registers (or a user is otherwise able to place an order using) a TRC-20 token whose `transfer()` implementation returns `false` on failure instead of reverting (e.g., insufficient balance from an internal accounting quirk, blacklist check, or a deliberately crafted malicious token) as an order input or fee token on the Tron `IntentGatewayV2`.
2. A user calls `placeOrder`, escrowing that token; `_orders[commitment][token]` is credited.
3. A solver fills the order on the destination chain and the settlement `RedeemEscrow` request is relayed back to the Tron chain.
4. `onAccept` → `withdraw(body, false)` executes; the token's `transfer()` call returns `(true, abi.encode(false))` at the low level (call itself does not revert, but the ERC-20 return value is `false`).
5. Because only `success` is checked (`(bool success,) = token.call(...); if (!success) revert TransferFailed();`), the code proceeds: `_orders[body.commitment][token] -= amount` and `_filled[body.commitment] = beneficiary` are executed, `EscrowReleased` is emitted — despite the beneficiary receiving zero tokens.
6. The escrowed tokens remain locked in the contract with no accounting path left to reclaim them for the solver or refund the user, since the order is now marked filled and its escrow already zeroed.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L693-714)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L463-477)
```text

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }
```
