Confirmed: `sdk/packages/core/contracts/apps/IntentGatewayV2.sol` also lacks the `balBefore`/`balancesBefore` actual-received-amount tracking that the current `evm/src/apps/IntentGatewayV2.sol` has. Both this SDK-embedded copy and the Tron deployment (`evm/tron/contracts/apps/IntentGatewayV2.sol`) still use the pre-mitigation pattern.

### Title
`IntentGatewayV2.placeOrder` credits escrow with the requested amount instead of the amount actually received, stranding solver payouts for fee-on-transfer tokens - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`, also present in `sdk/packages/core/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` (and the copy vendored under `sdk/packages/core/contracts/apps/`) escrow-credits the token amount specified in `order.inputs[i].amount` (net of protocol fee) after calling `safeTransferFrom`/sweeping tokens, without ever measuring the contract's actual token balance before and after the transfer. This is architecturally identical to the BakerFi `removeStrategy()` bug: an operation that can yield less than the nominal amount (there, `undeploy()`; here, an ERC20 transfer from a fee-on-transfer or deflationary token) is trusted to have delivered the full nominal amount, and that unchecked nominal amount is then used to update internal accounting (`strategyAssets`/`_allocateAssets` there, `_orders[commitment][token]` here) that a later privileged consumer relies on to move real funds.

### Finding Description
In the non-predispatch branch of `placeOrder`:
```solidity
// evm/tron/contracts/apps/IntentGatewayV2.sol:450-469
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
    unchecked { ++i; }
}
``` [1](#0-0) 

`reducedInputs[i].amount` is derived purely from `order.inputs[i].amount` minus the protocol fee — it is never adjusted to what `IERC20(token).balanceOf(address(this))` actually increased by. For any fee-on-transfer, rebasing, or deflationary ERC20, `safeTransferFrom` moves less than `order.inputs[i].amount` into the contract, yet the full nominal amount is credited to escrow.

The predispatch branch has the same gap: it computes `dust = balance - requiredAmount` (an excess check) but still credits `reducedInputs[i].amount` — the nominal, pre-transfer figure — rather than what the gateway itself received after `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` runs the token's `transfer()` call, which is equally subject to fee-on-transfer loss: [2](#0-1) 

The escrow entry is later trusted at face value by `withdraw()`, which transfers `body.tokens[i].amount` (sourced from the inflated `_orders[commitment][token]`) straight out to the beneficiary without any balance check:
```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    ...
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}
_orders[body.commitment][token] -= amount;
``` [3](#0-2) 

This is the exact "trust the nominal amount, not the delivered amount" failure the BakerFi report describes: `removeStrategy()` called `_allocateAssets(strategyAssets)` using the pre-undeploy amount instead of the actual `receivedAmount` from `undeploy()`.

Notably, the current `evm/src/apps/IntentGatewayV2.sol` has already been hardened against exactly this class of bug — it snapshots `balancesBefore[i]` and computes `received = IERC20(token).balanceOf(address(this)) - balancesBefore[i]` before mutating `order.inputs[i].amount` and computing the commitment/escrow (confirmed via the project's own `FeeOnTransferToken` regression tests). That fix was never propagated to the Tron contract or the SDK-vendored copy, leaving those deployments in the pre-mitigation state. [4](#0-3) 

### Impact Explanation
Escrow accounting for a fee-on-transfer input token becomes systematically over-credited relative to the tokens the gateway actually holds. Once any solver fills and redeems escrow for such an order (locally via `_cancelSameChain`/local withdraw, or cross-chain via the `RedeemEscrow` `onAccept` path calling `withdraw()`), the contract attempts to pay out more than it holds for that token. In a single-order-per-token scenario this reverts and permanently freezes the user's real (smaller) deposit inside the contract, since `_orders[commitment][token]` can never be fully drained to zero. In a multi-order scenario where the same fee-on-transfer token is used across several concurrent orders, the shortfall from one inflated order is paid out of token balance that rightfully belongs to other orders' escrow, i.e. later legitimate redemptions/cancellations fail or are shorted — a cross-order insolvency that can be triggered by any unprivileged user simply by placing an order denominated in a token with transfer fees (deflationary/rebasing/tax tokens are common on both EVM chains and Tron). This is a concrete freezing-of-funds / accounting-insolvency bug reachable from a single `placeOrder` call by any user.

### Likelihood Explanation
Reachable by any unprivileged account submitting a normal `placeOrder` transaction with a fee-on-transfer/deflationary ERC20 as an input — no privileged role or governance action is required. Tron in particular hosts TRC20 tokens with transfer taxes/burns, and the intent gateway's token whitelist (if any) is a deployment/governance configuration, not a protocol-level guarantee that only "clean" tokens will ever be used, matching the same low-effort trigger condition (`removeStrategy`/`undeploy` on a leverage strategy) rated Medium in the original report.

### Recommendation
Mirror the fix already applied in `evm/src/apps/IntentGatewayV2.sol`: in `placeOrder`, snapshot the gateway's token balance immediately before each transfer/sweep and credit escrow (and compute the commitment) using the measured post-transfer delta (`balanceOf(address(this)) after − before`) rather than the nominal `order.inputs[i].amount`. Apply the same balance-before/after measurement to the predispatch sweep path's final `transfer()` into the gateway. Port this fix to both `evm/tron/contracts/apps/IntentGatewayV2.sol` and `sdk/packages/core/contracts/apps/IntentGatewayV2.sol` so all deployed copies of the intent gateway are consistent.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron contract) with a 1%-fee-on-transfer ERC20/TRC20 `FOT` as an allowed input token.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`. `safeTransferFrom` moves only 990e18 into the gateway (1% burned/fee), but `_orders[commitment][FOT] += reducedInputs[0].amount` credits (up to) 1000e18 (minus protocol fee, if any) — more than the 990e18 actually held.
3. A solver fills the order and the `RedeemEscrow` request reaches `onAccept` → `withdraw()`, which attempts `token.transfer(beneficiary, escrowedAmount)` for the inflated escrowed amount.
4. If this is the only order in that token, the transfer reverts (`TransferFailed`) because the gateway's real FOT balance (990e18) is less than the credited escrow — the user's real deposit is stuck, `_orders[commitment][FOT]` can never be zeroed. If other orders share the same token, the shortfall is paid from their escrow, corrupting accounting for unrelated users.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L291-329)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
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
