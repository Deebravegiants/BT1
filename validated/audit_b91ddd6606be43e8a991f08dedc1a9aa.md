Confirmed: this is a live, deployed contract on TRON (Nile testnet address `TT4CjjHw7QgLbE9wKtYEopid1YqePkbAfb`, mainnet-deployable via `evm/tron/README.md`). Unlike the main `evm/src/apps/IntentGatewayV2.sol`, which was hardened against fee-on-transfer tokens with balance-before/after checks (confirmed by tests in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`), the TRON port at `evm/tron/contracts/apps/IntentGatewayV2.sol` was not updated with the same fix and still trusts the nominal `order.inputs[i].amount` for commitment hashing and escrow accounting.

### Title
Fee-on-transfer ERC20 tokens break escrow accounting in the TRON IntentGatewayV2 `placeOrder`, enabling escrow under-collateralization and solver theft - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The TRON deployment of `IntentGatewayV2.placeOrder` computes the order commitment and credits `_orders[commitment][token]` using the user-declared `order.inputs[i].amount`, then pulls tokens via a raw `safeTransferFrom`/low-level call without verifying how much the contract actually received. For fee-on-transfer (or otherwise deflationary) TRC-20/ERC-20 tokens, the contract will receive less than the escrowed/committed amount, creating an accounting mismatch between the recorded escrow and the actual token balance held.

### Finding Description
In `placeOrder` (`evm/tron/contracts/apps/IntentGatewayV2.sol`), when there is no predispatch call, tokens are pulled directly with: [1](#0-0) 
which for the non-predispatch path uses `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount` — the *requested* amount, not the amount actually received. The commitment hash itself, computed earlier via `keccak256(abi.encode(order))`, is also built from the nominal, unreduced-for-fee `order.inputs[i].amount` (only reduced for protocol fee, not transfer fee): [2](#0-1) 

The predispatch path has an identical flaw: it sweeps `balance = IERC20(token).balanceOf(dispatcher)` from the call dispatcher but still credits escrow with `reducedInputs[i].amount` (the nominal requested amount) rather than the amount swept, so the same shortfall problem occurs whenever the predispatch itself routes through a fee-on-transfer token: [3](#0-2) 

This is a regression relative to the hardened main EVM contract, `evm/src/apps/IntentGatewayV2.sol`, which explicitly measures `balanceOf` before and after every transfer and mutates `order.inputs[i].amount` to the actual received value before computing the commitment and crediting escrow: [4](#0-3) [5](#0-4) 
This exact defense (comment: "For fee-on-transfer tokens, the gateway receives less than the requested amount...") was added to the main contract but never ported to the TRON fork.

Downstream, `withdraw()` in the TRON contract pays out the full recorded `body.tokens[i].amount` on fill/cancel using a raw low-level `token.call(...)` transfer: [6](#0-5) 
Since the escrow ledger (`_orders[commitment][token]`) was credited with more than the contract actually holds for that token, the ledger becomes internally inconsistent across all orders sharing that token, and a later withdrawal can drain funds belonging to other users/orders (insolvency), or simply revert once the shortfall is discovered, freezing legitimate orders.

### Impact Explanation
This is reachable by any unprivileged user calling `placeOrder` with a fee-on-transfer token as an input asset — no special privileges required. The impact is direct loss of funds / bad debt to the pool of escrowed tokens shared across all orders on that TRON deployment: the recorded escrow total for a given token can exceed the actual token balance held by the contract, so honest solvers/users filling or cancelling other orders in the same token can be shorted or a race can drain the shared token balance, leaving some orders permanently unable to be paid out in full (frozen/lost funds). This matches the "Loss of funds ... small amount of bad debt" impact pattern described in the source report, generalized to the intents escrow model.

### Likelihood Explanation
Likelihood is High for any TRON deployment that allows arbitrary/permissionless input tokens (which the intent gateway design supports, since `order.inputs[i].token` is an arbitrary address chosen by the order creator). Fee-on-transfer and deflationary tokens are common on TRC-20 chains; a malicious or unaware user placing an order with such a token as input immediately creates the accounting drift without any attacker collusion needed — it happens on ordinary use of the affected token type.

### Recommendation
Port the fix already present in `evm/src/apps/IntentGatewayV2.sol` to the TRON contract: measure `balanceOf(address(this))` (and `balanceOf(dispatcher)` in the predispatch/sweep path) before and after each transfer, mutate `order.inputs[i].amount`/`reducedInputs[i].amount` to the actually-received amount, and only then compute the commitment hash and credit `_orders[commitment][token]`. This keeps the on-chain escrow ledger consistent with the tokens the contract actually custodies, exactly as done in `evm/src/apps/IntentGatewayV2.sol:291-329`.

### Proof of Concept
1. Deploy a fee-on-transfer TRC-20 token (e.g. 1% fee on `transfer`/`transferFrom`) on the TRON network where `IntentGatewayV2` (`TT4CjjHw7QgLbE9wKtYEopid1YqePkbAfb`) is deployed.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and no predispatch.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes, but due to the 1% fee, the gateway contract's FOT balance only increases by `990e18`.
4. `_orders[commitment][FOT]` is nonetheless credited with the full (protocol-fee-adjusted) `reducedInputs[i].amount` derived from `1000e18`, not `990e18`.
5. When a solver fills the order (or the user cancels) and `withdraw()` is called, the contract attempts to pay out the full recorded escrow amount for FOT, which exceeds the actual FOT balance held by the contract for that order once other orders' escrow is accounted for — draining shared token balance / reverting and freezing funds for other order holders in the same token.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L356-386)
```text
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-469)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L291-306)
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
