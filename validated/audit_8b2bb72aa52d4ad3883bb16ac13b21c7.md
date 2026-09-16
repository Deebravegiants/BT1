## Title
Tron `IntentGatewayV2.placeOrder` credits escrow from declared amounts instead of verified transfer deltas, enabling unbacked escrow / theft of solver funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` computes the on-chain escrow balance (`_orders[commitment][token]`) and the order commitment hash directly from the user-declared `order.inputs[i].amount`, then calls `IERC20.safeTransferFrom` for that same declared amount without ever checking that the contract's token balance actually increased by that amount. This is the exact bug class described in the MonoX report: liquidity/escrow accounting trusts the declared transfer amount rather than the measured balance delta, so a malicious or non-standard ERC20 supplied as an order input can leave the escrow under-collateralized while the recorded commitment claims it is fully funded.

### Finding Description
In `placeOrder`, the reduced input amounts used for both the commitment hash and the escrow ledger are derived purely from `order.inputs[i].amount` (the user-supplied, undeclared-as-verified figure): [1](#0-0) 

The token transfer in the non-predispatch path then blindly calls `safeTransferFrom` for `order.inputs[i].amount` and immediately credits the escrow with `reducedInputs[i].amount` — with no balance check before/after the transfer: [2](#0-1) 

The predispatch path similarly checks only that the dispatcher's balance is `>= requiredAmount` (a pre-existing balance, not proof that this specific transfer moved that much) and still credits `reducedInputs[i].amount` unconditionally: [3](#0-2) 

Later, `withdraw()` pays out `body.tokens[i].amount` — the value stored in `_orders`, i.e., the *declared* amount — not the contract's actual token balance: [4](#0-3) 

This is precisely analogous to the MonoX `addLiquidityPair` bug: `safeTransferFrom` only checks that the call returned success/no-revert (per OpenZeppelin's `SafeERC20`), it does not verify the magnitude actually moved. Any ERC20 whose `transferFrom` transfers less than requested (deliberately malicious, or simply a standard fee-on-transfer/rebasing token) will cause the gateway to record an escrow credit that is not backed by an equivalent token balance.

Notably, the primary EVM `IntentGatewayV2.sol` (non-Tron) was hardened against this exact issue — it snapshots `balanceOf` before/after every `safeTransferFrom` and mutates `order.inputs[i].amount` to the actual received delta before computing the commitment and crediting escrow: [5](#0-4) 

The Tron variant is a separate, out-of-sync implementation that never received this fix, and it is reachable by any unprivileged user submitting `placeOrder` with an arbitrary ERC20 (including a self-deployed malicious token) as an input asset.

### Impact Explanation
A user can place an order specifying a malicious or fee-manipulating ERC20 as an input token. The order's commitment and stored escrow balance reflect the full declared amount, while the actual tokens held by the gateway can be arbitrarily smaller (or zero). A solver, observing the on-chain `_orders` escrow entry as proof of available collateral, fills the order by delivering real output tokens to the user/beneficiary. When the solver later attempts to redeem the escrowed input (via `withdraw()` after `RedeemEscrow`/`RefundEscrow` delivery), the contract attempts to transfer out the recorded (unbacked) amount — this either reverts (permanently freezing/DOSing that settlement, since `_filled` is already set) or, if the token is designed to under-report/over-mint elsewhere, drains real token reserves from the contract at the solver's/other users' expense. This is unbacked-credit style fund theft/freezing directly reachable from a single `placeOrder` transaction, matching Impact 4 / Likelihood 4 severity of the referenced MonoX finding.

### Likelihood Explanation
`placeOrder` is a fully public, unprivileged entry point that accepts an arbitrary ERC20 address as `order.inputs[i].token`. No allow-list or verification of token behavior is enforced before escrow crediting. Any attacker can deploy a trivial ERC20 with a manipulated `transferFrom` (as in the report's `EvilERC20` example) and immediately exploit this on the live Tron deployment. Likelihood is high.

### Recommendation
Apply the same fix already present in `evm/src/apps/IntentGatewayV2.sol` to the Tron variant: before crediting `_orders[commitment][token]` (and before computing the commitment hash), snapshot `IERC20(token).balanceOf(address(this))` (or the dispatcher, in the predispatch branch) immediately before and after each `safeTransferFrom`, and use the measured delta — not the declared `amount` — for both the commitment and the escrow credit, mirroring: [5](#0-4) 

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC20 whose `transferFrom` always moves `0` (or `1` wei) regardless of the `amount` argument, but returns `true`.
2. Attacker calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs = [{token: EvilToken, amount: 1_000_000e18}]` and a legitimate `output` asset/amount that a solver will find attractive.
3. `placeOrder` computes `reducedInputs[0].amount ≈ 1_000_000e18` (minus protocol fee), calls `safeTransferFrom(attacker, gateway, 1_000_000e18)` which succeeds while transferring ~0 tokens, then sets `_orders[commitment][EvilToken] = reducedInputs[0].amount` — a value far exceeding the gateway's actual `EvilToken` balance. [2](#0-1) 
4. A solver, trusting the escrow ledger, fills the order and transfers real output tokens to the beneficiary.
5. On settlement, `withdraw()` attempts to pay the solver `body.tokens[0].amount` (the unbacked declared amount) of `EvilToken`, which the gateway does not actually hold, causing the payout to revert (solver's legitimate output funds are permanently lost with no compensating input) or, depending on token implementation, undercollateralized token accounting can be exploited further. [4](#0-3)

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-700)
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
