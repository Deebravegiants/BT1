### Title
Fee-on-transfer tokens cause escrow over-crediting in Tron `IntentGatewayV2.placeOrder` (missing balance-delta check present in the EVM version) - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits `_orders[commitment][token]` escrow accounting using the pre-transfer, requested `order.inputs[i].amount` (minus protocol fee) instead of the amount the contract actually received. The mainline EVM `IntentGatewayV2.sol` was hardened against exactly this class of bug by snapshotting balances before/after each transfer and mutating `order.inputs` to the *actual received* amount before computing fees, the commitment, and escrow credit. The Tron fork does not carry this fix.

### Finding Description
In the non-predispatch branch of `evm/tron/contracts/apps/IntentGatewayV2.sol`: [1](#0-0) 

the contract does:
```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
...
_orders[commitment][token] += reducedInputs[i].amount;
```
`reducedInputs[i].amount` is derived earlier purely from `order.inputs[i].amount` (the user-requested amount) reduced only by the protocol fee bps, computed *before* any transfer occurs: [2](#0-1) 

For a fee-on-transfer (deflationary) ERC20 token, `safeTransferFrom` moves `order.inputs[i].amount` out of the user's wallet, but the gateway contract actually receives less than that (the transfer fee is burned/redirected in transit). The escrow ledger `_orders[commitment][token]` is nonetheless credited with the full pre-fee `reducedInputs[i].amount`, which is now larger than the tokens the contract actually holds for that commitment.

The predispatch branch has a partial mitigation (it checks `balance < requiredAmount` at the dispatcher before sweeping), but it still credits escrow with `reducedInputs[i].amount` rather than the balance actually landing in the gateway after the final `transferCalls` sweep from dispatcher → gateway, so a second-hop transfer fee on that sweep is also uncaptured: [3](#0-2) 

By contrast, the mainline EVM `IntentGatewayV2.sol` explicitly fixes this by snapshotting `balanceOf(this)` before and after each `safeTransferFrom`, and mutating `order.inputs[i].amount` to the actual delta before fees/commitment/escrow are computed: [4](#0-3) 
This fix (and equivalent double-fee-on-transfer handling in the predispatch path, lines 260-311 of the same file) is not present in `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Impact Explanation
Escrow accounting for a given `(commitment, token)` becomes greater than the tokens the contract actually holds. Because `_orders[commitment][token]` is a shared ledger across all orders denominated in that token, this over-crediting creates unbacked liabilities: when solvers fill orders and the protocol later attempts to pay out/withdraw the escrowed amount for this or other orders in the same token, the contract can run short of actual token balance, causing reverts (denial of service / stuck funds) for legitimate order withdrawals, or — depending on withdrawal ordering — allowing some claimants to drain the shared pool at the expense of others, effectively socializing the fee-on-transfer loss onto other users' escrowed funds. This is a concrete insolvency/fund-freezing risk within an unprivileged, permissionless order-placement flow reachable by any user submitting a single `placeOrder` transaction with a fee-on-transfer token.

### Likelihood Explanation
Any external, unprivileged account can trigger this by calling `placeOrder` with a fee-on-transfer/deflationary ERC20 as an input token — no special privileges, governance, or admin action required. The condition is deterministic (any transfer-fee token triggers it every time), making likelihood high whenever the deployment does not strictly allowlist non-fee-on-transfer tokens.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: record `balanceOf(address(this))` (or dispatcher balance for the predispatch sweep) before and after each token transfer, mutate `order.inputs[i].amount` to the actual received delta, and derive `reducedInputs`/`commitment`/escrow credit from that actual-received amount rather than the pre-transfer requested amount, in both the direct-transfer and predispatch branches of `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with a fee-on-transfer ERC20 token `FOT` (e.g., 1% transfer fee) as a supported input asset.
2. User approves the gateway for `1000 FOT` and calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`.
3. `safeTransferFrom` moves `1000e18` intent from the user, but due to the 1% fee, the gateway's actual `FOT` balance only increases by `990e18`.
4. `_orders[commitment][FOT]` is nonetheless credited with `reducedInputs[0].amount` (≈`1000e18` minus only the protocol fee, not the transfer fee) — i.e., escrow records more `FOT` than the contract holds.
5. Repeating this (or combined with other orders in the same token) causes the sum of escrowed balances to exceed `FOT.balanceOf(gateway)`, so a later legitimate `withdraw`/fill payout in `FOT` reverts due to insufficient balance, freezing funds for other order participants.

(This mirrors the fee-on-transfer test coverage that exists for the fixed EVM contract, e.g. `testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, which has no Tron-side equivalent because the Tron contract lacks the corresponding fix.) [5](#0-4)

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
