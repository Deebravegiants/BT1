Based on my research, the strongest structural analog is the `IntentGatewayV2` dust-sweep logic in `evm/src/apps/IntentGatewayV2.sol` (predispatch path) and `evm/tron/contracts/apps/IntentGatewayV2.sol`, where escrow accounting is derived from a **shared contract's balance snapshot** rather than an isolated per-order/per-payment address — the same bug class described in the report (a balance-based check on a shared/fixed address can be polluted by unrelated transfers).

### Title
Escrow/dust accounting via shared-address `balanceOf` snapshot can be polluted by unrelated inbound transfers - (File: evm/src/apps/IntentGatewayV2.sol, evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder`'s predispatch path (and the Tron fork's `dispatcher`-based escrow variant) computes how much of a token to escrow by reading `balanceOf` on a shared address (the gateway itself, or the `ICallDispatcher`) before/after an arbitrary `predispatchCall`, then treats anything above the `requiredAmount` as "dust" to sweep into escrow/protocol accounting [1](#0-0) . In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the balance is read directly off the `dispatcher` address and the delta above `requiredAmount` is emitted as `DustCollected` and swept via a generic `Call` before the reduced amount is credited to escrow [2](#0-1) .

### Finding Description
This is directly analogous to the `ERC20BalanceGteEnforcer` bug: the contract infers "the intended amount arrived" purely from an address's balance delta, without binding that balance to a specific payer or a single-use address. The `dispatcher`/gateway address is a long-lived, shared contract that legitimately receives funds from many different orders and many different users concurrently (and, on the Tron variant, arbitrary `predispatchCall` swaps run before the balance is re-read). Any other actor's token transfer landing on that same address between the "before" and "after" snapshot — from an unrelated order's leftover dust, a pull-payment, a reward payout, or simply another concurrent `placeOrder`/`fillOrder` call — inflates the measured balance and is silently absorbed into the current caller's escrow/dust accounting: `uint256 dust = balance - requiredAmount; if (dust > 0) emit DustCollected(token, dust); ... _orders[commitment][token] += reducedInputs[i].amount;` [3](#0-2) . Because escrow crediting and commitment building both derive from this snapshot rather than from a `safeTransferFrom` amount tied to `msg.sender`, the accounting cannot distinguish "the actual order payer's funds" from "any token that happens to be sitting at the shared address," exactly the "side payment vs. intended payment" ambiguity flagged in the ERC20BalanceGteEnforcer report.

### Impact Explanation
If a shared balance can be inflated by a concurrent transaction (e.g., another user's `placeOrder`/`fillOrder`/`predispatchCall` swap output landing at the same address in the same block, or an ERC-777/callback-style token triggering a transfer mid-call), the escrow ledger (`_orders[commitment][token]`) and/or the `DustCollected` sweep can misattribute funds, potentially crediting one order's commitment with tokens that belong to another party or letting an attacker manufacture apparent "dust" to redirect funds intended for a different order. This risks fund misallocation/theft within the intents escrow, a Medium/High-severity issue under the token-bridge/intents-escrow scope.

### Likelihood Explanation
Reachability is straightforward: `placeOrder` and `fillOrder` are unprivileged, externally callable entry points, and the vulnerable pattern is specifically exercised when `order.predispatch.call` is non-empty (arbitrary external call executed before the balance is re-measured) — an attacker-controlled or attacker-influenced order field [4](#0-3) . Exploiting it requires an attacker to land a transfer to the shared address within the same transaction window (e.g., via `predispatchCall` itself, or a reentrant/callback token), which is plausible for fee-on-transfer/callback tokens the codebase already explicitly supports (see the fee-on-transfer accounting tests) [5](#0-4) .

### Recommendation
Do not infer payment/escrow amounts from a shared address's `balanceOf` delta. Instead, tie every credited amount directly to an authenticated transfer (`safeTransferFrom(msg.sender, address(this), amount)` with the actual received amount checked against a per-call temporary balance snapshot that is read and consumed atomically, not shared across concurrent calls), or route `predispatchCall` outputs to a fresh, single-use, per-order address before sweeping, analogous to the `paymentAddress` mitigation recommended in the source report. At minimum, use a reentrancy-safe, per-transaction transient balance capture that cannot be polluted by any other concurrently executing call in the same block/mempool.

### Proof of Concept
1. Attacker observes a pending `placeOrder(order)` call whose `order.predispatch.call` triggers an external swap that lands output tokens at the gateway/dispatcher address before the "after" balance is read.
2. Attacker crafts or times a second transaction (e.g., their own `placeOrder`/token transfer) so that its token transfer to the same shared address is included in the same block, before the victim's "after" `balanceOf` snapshot.
3. The victim's `dust = balance - requiredAmount` computation now includes the attacker's unrelated tokens, which get emitted as `DustCollected` / credited into `_orders[commitment][token]`, or conversely the attacker's own order under-escrows because their tokens were consumed by someone else's dust sweep.
4. Exact confirmation of full exploit mechanics (ordering guarantees, mempool assumptions) would require deeper reproduction in a Devin session with test execution, since this analysis is based on static code reading only.

### Citations

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L181-238)
```text
        // Setup order inputs (what will be escrowed)
        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: minDaiAmount});

        // Setup order output assets (what filler will provide on destination chain)
        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({
            token: bytes32(uint256(uint160(address(usdc)))),
            amount: 2000 * 1e6 // 2000 USDC
        });

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        // Create order
        Order memory order = Order({
            user: bytes32(0), // Will be set by contract
            source: "", // Will be set by contract
            destination: abi.encodePacked("DEST_CHAIN"),
            deadline: 0,
            nonce: 0, // Will be set by contract
            fees: 0,
            session: address(0),
            predispatch: predispatch,
            inputs: inputs,
            output: output
        });

        // Place order
        vm.startPrank(user);

        // Record events
        vm.recordLogs();

        uint256 daiBalanceBefore = dai.balanceOf(address(intentGateway));

        intentGateway.placeOrder{value: ethAmount}(order, bytes32(0));

        uint256 daiBalanceAfter = dai.balanceOf(address(intentGateway));

        vm.stopPrank();

        // Verify DAI was received
        assertGe(daiBalanceAfter - daiBalanceBefore, minDaiAmount, "Minimum DAI not escrowed");

        // Check for DustCollected event
        Vm.Log[] memory entries = vm.getRecordedLogs();
        bool dustCollectedFound = false;

        for (uint256 i = 0; i < entries.length; i++) {
            if (entries[i].topics[0] == keccak256("DustCollected(address,uint256)")) {
                dustCollectedFound = true;
                break;
            }
        }

        assertTrue(dustCollectedFound, "DustCollected event should be emitted");
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L420-446)
```text
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2479)
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
```
