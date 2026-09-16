### Title
Fee-on-transfer tokens inflate escrow accounting beyond actual balance held in Tron IntentGatewayV2 `placeOrder` - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` transfers input tokens via `safeTransferFrom` using the user-specified `order.inputs[i].amount`, but credits the escrow mapping `_orders[commitment][token]` with `reducedInputs[i].amount` — a value derived purely from the *requested* amount (minus an optional protocol-fee bps deduction) — without ever measuring the actual token balance the gateway received. For fee-on-transfer (deflationary) ERC-20 tokens, the physical balance received is strictly less than the requested amount, so the escrow ledger overstates the tokens actually custodied by the contract.

### Finding Description
In `placeOrder`'s non-predispatch branch: [1](#0-0) 

the contract does:
```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
...
_orders[commitment][token] += reducedInputs[i].amount;
```
`reducedInputs[i].amount` is computed earlier purely from `order.inputs[i].amount` reduced by `protocolFeeBps` — with no balance check: [2](#0-1) 

There is no `balanceOf` snapshot before/after the transfer, unlike the fixed EVM-mainline `IntentGatewayV2.sol`, which explicitly measures actual received amounts and mutates `order.inputs` to match reality before crediting escrow or computing the commitment: [3](#0-2) [4](#0-3) 

This confirms the Tron file lacks the fee-on-transfer safeguard present in the canonical implementation, and is a regression/divergence between the two copies of the same contract logic. The escrow map `_orders[commitment][token]` becomes an over-credited (unbacked) IOU for that order commitment.

### Impact Explanation
`_orders[commitment][token]` is the single source of truth used later during `withdraw` (invoked from `cancelOrder`, `onAccept` for `RedeemEscrow`/`RefundEscrow`) to pay out physical tokens from the gateway's pooled balance to a solver/filler or back to the user. Because the escrow accounting for a fee-on-transfer token input is inflated above what the contract actually holds, an order placed with such a token creates a shortfall: the gateway is contractually obligated (per its own bookkeeping) to pay out more tokens for that token address than it possesses. Since all orders for the same ERC-20 share one pooled contract balance, this shortfall is paid out of other users' legitimately escrowed funds for that same token — i.e., permanent loss/theft of funds for other depositors, or insolvency causing later legitimate withdrawals to revert. This satisfies "concrete theft or permanent freezing of funds" resulting from a single `placeOrder` transaction with an ordinary fee-on-transfer token, reachable by any unprivileged user.

### Likelihood Explanation
Likelihood is high wherever fee-on-transfer/deflationary tokens are permitted as intent inputs: the vulnerable code path is the default, non-predispatch branch of `placeOrder`, requiring no special privileges — any user can place an order using such a token and immediately create the inflated escrow record. No governance or admin action is needed, and the bug is purely arithmetic/accounting, deterministic and reproducible on every call with such a token.

### Recommendation
Mirror the fix already present in the canonical `evm/src/apps/IntentGatewayV2.sol`: snapshot `balanceOf(address(this))` before and after each `safeTransferFrom`, use the actual delta as the received amount, mutate `order.inputs[i].amount` (and thus the values fed into `reducedInputs`/commitment calculation) to reflect reality, and only credit `_orders[commitment][token]` with the amount actually held by the contract.

### Proof of Concept
1. Deploy a 1%-fee ERC-20 (`FeeOnTransferToken`) analogous to the test helper already present in the test-suite for the canonical contract.
2. User calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and `protocolFeeBps = 0`.
3. `safeTransferFrom(user, gateway, 1000e18)` executes; gateway physically receives only `990e18` (1% fee retained by token).
4. `reducedInputs[0].amount` remains `1000e18` (no protocol fee to deduct), and `_orders[commitment][FOT] += 1000e18` is recorded — 10e18 more than the gateway actually holds.
5. When this order (or another sharing the same token pool) is later filled/redeemed/cancelled via `withdraw`, the sum of all `_orders[...][FOT]` credits exceeds the gateway's real `FOT` balance, causing either reverts (DoS/freezing for legitimate withdrawers) or, if paid out sequentially, the last withdrawer's funds — which came from a different depositor's real balance — to be siphoned away, i.e. theft of pooled token funds. [5](#0-4)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L356-385)
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

**File:** evm/src/apps/IntentGatewayV2.sol (L363-373)
```text
        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2441-2493)
```text
    function testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived() public {
        // Deploy a 1% fee-on-transfer token
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% = 100 bps
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 expectedReceived = inputAmount - (inputAmount * 100) / 10000; // 990

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 900 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 100,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        fot.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Gateway should hold only what it actually received
        assertEq(
            fot.balanceOf(address(intentGateway)), expectedReceived, "Gateway balance should match received amount"
        );

        // Reconstruct the order as placeOrder would have mutated it
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = expectedReceived;
        bytes32 commitment = keccak256(abi.encode(order));

        // Escrow should match actual received, not the user-specified amount
        assertEq(
            intentGateway._orders(commitment, address(fot)),
            expectedReceived,
            "Escrow should equal actual received amount"
        );
```
