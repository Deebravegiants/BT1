### Title
Fee-on-transfer tokens cause escrow over-crediting in Tron `IntentGatewayV2.placeOrder` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` does not measure actual received token balances after `safeTransferFrom` in the non-predispatch path, unlike the canonical EVM implementation which explicitly reconciles balances to support fee-on-transfer tokens.

### Finding Description
In the canonical `evm/src/apps/IntentGatewayV2.sol::placeOrder` (`ExtrinsicIntents`/base logic), the non-predispatch branch measures the actual amount received before crediting escrow and mutating `order.inputs[i].amount`: [1](#0-0) 
This ensures the escrow bookkeeping (and the commitment hash used later for fills/refunds) always matches what the gateway actually holds, verified by dedicated fee-on-transfer tests. [2](#0-1) 

The Tron deployment at `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`, however, only pre-computes `reducedInputs` by subtracting the protocol fee from the user-specified `order.inputs[i].amount` — it never reads `IERC20(token).balanceOf(address(this))` before/after the transfer in the non-predispatch branch: [3](#0-2) 
It then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount` — the protocol-fee-adjusted *requested* amount, not the *actually received* amount: [4](#0-3) 
For any fee-on-transfer ERC-20 (or any token whose `transferFrom` delivers less than the nominal amount), the contract's real token balance will be strictly less than what `_orders[commitment][token]` claims is escrowed, and less than what the commitment hash (built from the un-mutated `order.inputs`) promises to a solver/filler.

### Impact Explanation
`_orders[commitment][token]` is the internal escrow ledger that backs subsequent `RedeemEscrow`/`RefundEscrow` payouts to solvers or refunds to the user. Because it is inflated relative to the gateway's real balance for fee-on-transfer tokens, the contract becomes insolvent for that token: the first successful redeem/refund against this (or another) order can drain the shared token balance and leave a later legitimate redeemer's `safeTransfer` to fail or leave the gateway unable to pay out the full escrowed amount recorded on-chain, i.e. a permanent, unbacked accounting entry and potential fund loss/freezing for whichever party is paid last. This is a direct analog of the referenced report's root cause (assuming transfer amount == received amount) applied to an escrow ledger instead of an AMM liquidity calculation.

### Likelihood Explanation
Exploitation requires only a single unprivileged `placeOrder` call using a fee-on-transfer token as input — no special permissions, governance, or off-chain trust are needed. Any token with nonstandard transfer behavior (fee-on-transfer, rebasing-on-transfer) supplied as an order input on the Tron deployment triggers the discrepancy deterministically every time.

### Recommendation
Mirror the canonical EVM `IntentGatewayV2` logic in the Tron contract's non-predispatch branch: snapshot `balanceOf(address(this))` before `safeTransferFrom`, compute `received = balanceOf(address(this)) - balBefore`, and use `received` (minus protocol fee) both when crediting `_orders[commitment][token]` and when mutating `order.inputs[i].amount` prior to computing `commitment = keccak256(abi.encode(order))`, exactly as done for the predispatch branch's `DustCollected` reconciliation already present in the same file.

### Proof of Concept
1. Deploy a fee-on-transfer ERC-20 (e.g., 1% fee) and the Tron `IntentGatewayV2`.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and `protocolFeeBps = 0` (or nonzero, doesn't matter).
3. Gateway calls `IERC20(token).safeTransferFrom(msg.sender, address(this), 1000e18)`, but due to the 1% fee, the gateway's actual balance only increases by 990e18.
4. Contract executes `_orders[commitment][token] += reducedInputs[0].amount` = 1000e18 (or 1000e18 minus protocol fee), not 990e18.
5. `_orders[commitment][token]` now claims 1000e18 (or close to it) is escrowed, while the gateway only physically holds 990e18 of that token.
6. When a solver later fills and redeems the escrow (or the order is cancelled/refunded), `safeTransfer` for the full recorded amount will either revert (freezing the order/solver's expected payout) or succeed by consuming FOT balance escrowed for other orders/users, causing loss to those other order holders — an unbacked/insolvent escrow ledger.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L312-328)
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-468)
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
```
