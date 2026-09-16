### Title
Escrow accounting in Tron `IntentGatewayV2.placeOrder` credits requested amounts instead of actually-received amounts for fee-on-transfer / non-standard tokens, causing insolvent escrow and reverting withdrawals - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits the internal `_orders` escrow ledger with the *requested* `order.inputs[i].amount` (reduced only by the protocol fee), but for the non-predispatch path it pulls tokens via a plain `safeTransferFrom` without ever checking how much the gateway actually received. For fee-on-transfer, rebasing, or any deflationary ERC20, the contract's real token balance will be lower than what it just credited to escrow, exactly mirroring the root cause described in the referenced Merkl-claim report (crediting/forwarding a nominal amount instead of the balance actually received).

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the non-predispatch branch of `placeOrder` does: [1](#0-0) 

```solidity
} else {
    for (uint256 i; i < inputsLen;) {
        if (order.inputs[i].amount == 0) revert InvalidInput();
        address token = address(uint160(uint256(order.inputs[i].token)));
        if (token == address(0)) {
            if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
            msgValue -= order.inputs[i].amount;
        } else {
            IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
        }
        // Store reduced amount (after protocol fees) in escrow
        _orders[commitment][token] += reducedInputs[i].amount;
        ...
```

`reducedInputs[i].amount` is derived purely from `order.inputs[i].amount` (the caller-specified amount minus the protocol fee) computed earlier at [2](#0-1) , never from the gateway's actual post-transfer balance. If `token` charges a transfer fee (or otherwise delivers less than the nominal amount), `IERC20(token).safeTransferFrom` moves less than `order.inputs[i].amount` into the contract, yet `_orders[commitment][token]` is still incremented by the full `reducedInputs[i].amount`. The escrow ledger now overstates the gateway's real balance of that token.

This is functionally identical to the reported bug class: the code assumes "amount requested/claimed == amount actually received," and does not use a balance-before/balance-after delta to determine the true credited amount — exactly the flaw fixed by the recommended diff in the Merkl report.

Notably, the mainline EVM contract (`evm/src/apps/IntentGatewayV2.sol`) was hardened against this exact issue via a `balBefore`/`balanceOf(address(this))` delta check [3](#0-2) , confirming the codebase itself treats this as a known vulnerability class that was patched in one variant but left unpatched in the Tron variant.

Downstream, `withdraw()` in the same Tron contract naively transfers `body.tokens[i].amount` out of escrow without any balance check, and simply decrements `_orders[body.commitment][token] -= amount` [4](#0-3) . Once the ledger has been over-credited relative to the real balance, subsequent withdrawal or fill/cancel/refund calls for orders sharing that token's ledger will fail (revert) once the true balance is exhausted before the ledger reaches zero, permanently freezing the affected user's escrowed funds (their `_orders[commitment][token]` remains non-zero/reachable on paper but the contract lacks the funds to pay it out).

### Impact Explanation
Any unprivileged user calling `placeOrder` with a fee-on-transfer/deflationary ERC20 as an input token creates an escrow record that overstates the tokens actually held by the gateway. Because escrow credits (`_orders[commitment][token]`) are a *shared pool* only tracked per commitment/token but funded from a common contract balance, subsequent successful withdrawal/fill/cancel calls (for this or other orders using the same token) can drain the real balance before all committed escrow entries are honored, causing legitimate downstream `withdraw()` calls to revert with `TransferFailed`/`InsufficientNativeToken` due to insufficient balance — a permanent freezing of funds for the last claimant(s). This satisfies the "permanent freezing of funds" / "route unable to deliver messages" impact bar (Medium).

### Likelihood Explanation
Likelihood is Medium: it requires a fee-on-transfer, deflationary, or otherwise non-standard ERC20 to be configured/whitelisted as an intent input token. Any unprivileged user can place an order with such a token to trigger the discrepancy — no special privileges are required, only the token needs to be accepted by the gateway's order-input validation (which the contract does not otherwise restrict by token standard).

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: measure the gateway's token balance before and after `safeTransferFrom` in the non-predispatch branch, and use the actual delta (not the nominal `order.inputs[i].amount`) both for `reducedInputs` fee computation, the `commitment` hash, and the `_orders[commitment][token]` credit, e.g.:

```solidity
uint256 balBefore = IERC20(token).balanceOf(address(this));
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
```
and compute `reducedInputs`/`commitment` after this correction, consistent with `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Governance/admin (or permissionless config, depending on deployment) allows a fee-on-transfer ERC20 `FOT` (1% fee) as an intent input token on the Tron `IntentGatewayV2`.
2. User A calls `placeOrder` with `inputs = [{token: FOT, amount: 1000}]`. `safeTransferFrom` delivers only 990 FOT to the gateway, but `_orders[commitment][FOT] += reducedInputs[0].amount` credits (close to) 1000 (minus only the protocol fee, not the transfer fee).
3. Repeat with User B placing a similar order; the gateway's real FOT balance grows by 990 per order while the aggregate escrow ledger grows by ~1000 per order.
4. As orders are filled/cancelled and `withdraw()` is called sequentially, later withdrawals attempt to transfer amounts based on the inflated ledger; once the real FOT balance is depleted below what remaining `_orders` entries claim, `withdraw()`'s `token.call(...transfer...)` fails and reverts with `TransferFailed`, permanently freezing the beneficiary's escrowed tokens.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-385)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }
```
