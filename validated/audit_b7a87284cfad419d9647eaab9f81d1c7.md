### Title
Fee-on-transfer token accounting mismatch in Tron `IntentGatewayV2.placeOrder` leads to escrow over-crediting and stuck withdrawals - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` credits escrow (`_orders[commitment][token]`) using the user-declared `order.inputs[i].amount` (or the protocol-fee-reduced version of it) instead of the amount the contract actually received via `safeTransferFrom`. This is the same bug class as the Sherlock Gitcoin Allo.sol finding: for "fee on transfer" (deflationary) ERC20 tokens, the contract will record more tokens in escrow than it physically holds, causing later withdrawals to under-fund and revert.

### Finding Description
In `evm/src/apps/IntentGatewayV2.sol` (the canonical EVM contract), `placeOrder` explicitly guards against fee-on-transfer tokens by snapshotting balances before and after `safeTransferFrom` and using the *actual received* delta for both the commitment and the escrow bookkeeping: [1](#0-0) 

The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, omits this safeguard entirely. In the non-predispatch branch it calls `safeTransferFrom` for the full requested `order.inputs[i].amount` and then credits `_orders[commitment][token]` with `reducedInputs[i].amount` (the requested amount minus protocol fee), without ever checking the token balance actually received: [2](#0-1) 

The predispatch branch has the same issue — it computes `dust = balance - requiredAmount` for excess but never reduces the escrowed amount for a *shortfall* caused by transfer fees, and unconditionally credits `reducedInputs[i].amount`: [3](#0-2) 

Consequently, when a fee-on-transfer token is used as an order input, the contract's `_orders` mapping records a higher balance than what it actually holds in its own token balance.

### Impact Explanation
When the order is later settled — either via `withdraw()` on a `RedeemEscrow`/`RefundEscrow` request (`onAccept`) or via same-chain immediate cancellation — the contract attempts to `transfer` the full escrowed `amount` to the beneficiary/solver: [4](#0-3) 

Because the contract's actual token balance is lower than the recorded escrow amount (due to the transfer fee taken on the way in), this `token.call(...)` will either fail (reverting the whole withdrawal, permanently freezing the legitimately-received funds and the accompanying tx fees in the same loop) or, if the token silently returns `false`/succeeds with a partial transfer, leave the escrow mapping in an inconsistent state relative to actual holdings, which can starve other orders/tokens sharing the same contract balance. This matches the report's "Bob gets nothing, distribution reverts" scenario. The affected path is reachable by any unprivileged user simply calling `placeOrder` with a fee-on-transfer ERC20 as an input token — no admin/governance/relayer collusion required, satisfying the "permanent freezing of funds" criterion.

### Likelihood Explanation
Likelihood is Medium: it requires the deployment to support (or a solver/user to select) a fee-on-transfer ERC20 as an order input token on the Tron gateway. The main EVM `IntentGatewayV2.sol` and its extensive `FeeOnTransferToken` test suite show the protocol explicitly anticipates and defends against such tokens elsewhere, confirming this is a realistic, foreseen token class for this exact contract family — the Tron deployment is simply missing the fix that was applied to the primary EVM contract.

### Recommendation
Apply the same balance-snapshot pattern used in `evm/src/apps/IntentGatewayV2.sol` to the Tron contract: for each non-native input token, record `balanceOf(address(this))` before `safeTransferFrom` and after, use the delta as the actually-received amount, mutate `order.inputs[i].amount` accordingly before computing the commitment and before crediting `_orders[commitment][token]`. Apply the equivalent fix to the predispatch sweep path (compare against actual balance delta rather than only checking for `dust` on the excess side, and reduce escrow when the received amount is a shortfall rather than a surplus).

### Proof of Concept
1. Deploy a 1% fee-on-transfer ERC20 (mirroring `FeeOnTransferToken` used in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol` lines 2690-2735) and mint 10,000 tokens to `user`.
2. `user` approves `IntentGatewayV2` (Tron) for `inputAmount = 1000e18` and calls `placeOrder` with this token as `order.inputs[0]`.
3. Inside `placeOrder`, `IERC20(token).safeTransferFrom(msg.sender, address(this), 1000e18)` is invoked; due to the 1% fee, the contract's actual balance only increases by `990e18`.
4. `_orders[commitment][token]` is nonetheless set to `reducedInputs[0].amount` derived from `1000e18` (minus any protocol fee), i.e. an amount up to `1000e18`, exceeding the `990e18` actually held.
5. When `withdraw()` is later invoked (via `onAccept` RedeemEscrow/RefundEscrow, or same-chain `cancelOrder`), the `token.call(transfer(beneficiary, amount))` for the recorded (too-high) `amount` fails because the contract does not hold enough tokens, causing `revert TransferFailed()` and permanently freezing the escrowed funds (and any co-escrowed tx fees in the same loop, since `withdraw` reverts atomically).

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
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
