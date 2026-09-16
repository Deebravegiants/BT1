This confirms the vulnerability. The Tron variant of `IntentGatewayV2.placeOrder` never validates the actual token amount received from `safeTransferFrom` before crediting escrow — unlike the canonical EVM contract, which was patched to measure balances before/after transfer specifically to handle fee-on-transfer tokens.

### Title
Fee-on-transfer tokens cause escrow over-crediting and fund insolvency in Tron IntentGatewayV2.placeOrder - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron deployment of `IntentGatewayV2.placeOrder` credits escrow (`_orders[commitment][token]`) based on the user-requested `order.inputs[i].amount` (reduced only by protocol fee), instead of the actual balance the contract received via `safeTransferFrom`. For any ERC20 input token that charges a transfer fee (fee-on-transfer/deflationary token), the gateway will record more tokens in escrow than it actually holds.

### Finding Description
In the non-predispatch path of `placeOrder`: [1](#0-0) 
the contract calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally does `_orders[commitment][token] += reducedInputs[i].amount;` where `reducedInputs[i].amount` is derived from the pre-transfer `order.inputs[i].amount` minus only the protocol fee: [2](#0-1) 

No balance-before/balance-after check is performed, so if `token` deducts a fee on transfer, the gateway's actual holdings are less than `reducedInputs[i].amount`, yet escrow accounting assumes the full amount was received.

This is exactly the bug class flagged in the referenced Sherlock report for Mover's `HardenedTopupProxy._processTopup`, and the sibling non-Tron contract `evm/src/apps/IntentGatewayV2.sol` was explicitly hardened against this: it snapshots balances before transfer and mutates `order.inputs[i].amount` to the actual amount received before computing escrow/fees/commitment: [3](#0-2) 
This fix, and the dedicated `FeeOnTransferToken` regression tests validating it, exist only for the mainline EVM contract: [4](#0-3) 
The Tron contract at `evm/tron/contracts/apps/IntentGatewayV2.sol` never received this fix and still trusts the nominal input amount for escrow bookkeeping in both the predispatch dust-check path and the direct-transfer path.

The predispatch branch is similarly wrong: it computes `dust = balance - requiredAmount` off the dispatcher's balance (which is fine for detecting excess) but then also credits `_orders[commitment][token] += reducedInputs[i].amount` — again based on the nominal `order.inputs[i].amount`, not what was actually swept into the gateway.

### Impact Explanation
Escrow accounting becomes inflated relative to actual token holdings whenever a fee-on-transfer token is used as an order input on Tron. Because `_orders[commitment][token]` is the value used later for solver payout/withdrawal (`withdraw`, `cancelOrder`, `redeemEscrow`) via the shared `_orders` mapping, over-crediting causes either: (a) the gateway attempting to pay out more tokens than it actually holds for a given commitment, reverting or starving other orders' escrow of that same token, or (b) systemic insolvency across users sharing the same token, where earlier claims succeed and later legitimate claimants cannot be paid — a permanent freezing/loss of funds condition for other order holders sharing the token pool.

### Likelihood Explanation
Any user can place an order with a fee-on-transfer/deflationary ERC20 as an input asset by simply calling `placeOrder` — no privileged role is required, and Tron has an active ecosystem of such tokens (deflationary/rebasing/tax tokens are common). The trigger is a single unprivileged `placeOrder` call.

### Recommendation
Mirror the fix already applied in `evm/src/apps/IntentGatewayV2.sol`: record `IERC20(token).balanceOf(address(this))` before each `safeTransferFrom`, take the post-transfer balance difference as the actual received amount, and use that (not the nominal `order.inputs[i].amount`) both for the commitment hash and for crediting `_orders[commitment][token]`. Apply the same balance-diff approach to the predispatch sweep path so `_orders[commitment][token]` reflects tokens actually held by the gateway, not the requested amount.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee) on the Tron IntentGatewayV2's chain.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, approving the gateway for `1000e18`.
3. `IERC20(token).safeTransferFrom(msg.sender, address(this), 1000e18)` executes; due to the 1% fee, the gateway actually receives only `990e18`.
4. `_orders[commitment][token] += reducedInputs[0].amount` credits `1000e18` (minus only protocol fee, if any) to escrow, while the gateway's real `balanceOf(address(this))` for that token is `990e18`.
5. When the order is filled/withdrawn/redeemed against this commitment, the contract believes it can release `1000e18`-based accounting to solver/beneficiary while only holding `990e18`, producing a shortfall that either reverts (DoS on withdrawal) or drains balance belonging to other unrelated orders holding the same token, i.e. fund freezing/loss for other users. Compare directly to the passing test `testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived` for the non-Tron contract, which would fail if run against this Tron variant's equivalent logic.

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2494)
```text
    /// @notice Escrow correctly reflects actual received amount for fee-on-transfer tokens.
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
    }
```
