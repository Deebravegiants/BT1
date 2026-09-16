### Title
Escrow ledger credits requested amount instead of actual received amount for fee-on-transfer tokens in Tron IntentGatewayV2.placeOrder - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
In the Tron variant of `IntentGatewayV2.placeOrder`, the non-predispatch escrow path pulls tokens via `safeTransferFrom` using `order.inputs[i].amount`, but credits the internal escrow ledger `_orders[commitment][token]` with `reducedInputs[i].amount`, which is derived from the *requested* `order.inputs[i].amount`, not the amount actually received by the contract. For any ERC20 with transfer fees (fee-on-transfer tokens), this produces an escrow ledger that overstates the gateway's real token balance.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the direct-transfer branch of `placeOrder` does: [1](#0-0) 

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

`reducedInputs[i].amount` is computed earlier purely from `order.inputs[i].amount` minus the protocol fee percentage — it never accounts for tokens that deduct a transfer fee on `transferFrom`. If the token deducts, say, 1% on transfer, the gateway's real balance increase is less than `order.inputs[i].amount`, yet the ledger records the full (fee-adjusted-only) amount as escrowed and claimable by a filler/solver.

This is the exact bug class from the external report (strict/implicit assumption that transferred amount == requested amount), except here the accounting error is silent (no revert) and directly corrupts the internal escrow bookkeeping rather than merely reverting.

Contrast this with the canonical EVM implementation at `evm/src/apps/IntentGatewayV2.sol`, which explicitly snapshots balances before/after the transfer and mutates `order.inputs[i].amount` to the actual amount received before computing the commitment/escrow value: [2](#0-1) 

The Tron fork does not carry this fix through into its escrow-crediting logic for the non-predispatch path, and the predispatch path also computes `dust` against `requiredAmount` (the pre-fee target) rather than verifying what the IntentGateway itself actually receives after the second transfer leg from the dispatcher, compounding the issue: [3](#0-2) 

The Foundry test suite for the canonical EVM contract explicitly covers and validates the fee-on-transfer correctness (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, `testPlaceOrder_FeeOnTransferToken_WithProtocolFee`, `testPlaceAndFill_FeeOnTransferToken_RoundTrip`), confirming the design intent that escrow accounting must always track actual received balance — an invariant the Tron contract's `placeOrder` violates: [4](#0-3) 

### Impact Explanation
Because `_orders[commitment][token]` is the authoritative escrow ledger used to determine how much a filler/solver can redeem (via `RedeemEscrow`/`withdraw`) or how much a user can reclaim on cancellation, crediting more than the contract actually holds means:
- The gateway becomes under-collateralized for that token: the sum of all outstanding escrow claims can exceed the actual on-chain token balance.
- Whichever party redeems/cancels first can drain the real balance; subsequent legitimate claimants (fillers expecting payment, or users cancelling unfilled orders) will have their withdrawal revert (token balance insufficient) or be paid only partially, i.e., a permanent freezing/loss of funds for later claimants — an insolvency condition affecting anyone using a fee-charging ERC-20 as an order input on the Tron deployment.

### Likelihood Explanation
This triggers on any single `placeOrder` call using a token that charges a fee (or otherwise reduces value) on transfer as the input asset — no special privileges, governance, or multi-step attack chain are required. It is directly reachable by any unprivileged user submitting an order through the public `placeOrder` entry point, matching the "single submitted transaction" reachability bar. Likelihood is contingent on whether any deployed input token used with the Tron IntentGatewayV2 is fee-on-transfer, which is common enough among Tron-ecosystem TRC-20 tokens to be a realistic operational risk.

### Recommendation
Mirror the fix already implemented in `evm/src/apps/IntentGatewayV2.sol`: measure the contract's actual token balance immediately before and after each `safeTransferFrom` (and after the dispatcher-return transfer in the predispatch branch), and derive `reducedInputs`/escrow credit strictly from the measured received amount rather than the caller-supplied `order.inputs[i].amount`. Apply this consistently to both the direct-transfer branch and the predispatch branch of `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`.

### Proof of Concept
1. Deploy a fee-on-transfer TRC-20 token (e.g., 1% fee burned/redirected on every `transfer`/`transferFrom`), mirroring the `FeeOnTransferToken` test helper used for the canonical EVM contract.
2. User calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, having approved the gateway for `1000e18`.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; due to the 1% fee, the gateway's real FOT balance increases by only `990e18`.
4. Despite this, `_orders[commitment][FOT] += reducedInputs[0].amount`, where `reducedInputs[0].amount` is computed from the full `1000e18` (minus only the protocol fee bps, not the transfer fee) — the ledger now claims escrow of an amount the contract does not actually hold.
5. When a filler later redeems this escrow (via `RedeemEscrow`/`withdraw`), the contract will attempt to pay out more FOT than it received, causing either a revert for the last claimant in a multi-order scenario or a shortfall/insolvency if the gateway holds pooled balances across several orders of the same token. [5](#0-4)

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2441-2494)
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
    }
```
