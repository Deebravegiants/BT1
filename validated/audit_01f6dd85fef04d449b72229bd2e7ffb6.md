### Title
IntentGatewayV2 escrows the pre-fee requested amount instead of the actual received amount for fee-on-transfer input tokens, causing under-collateralized/unpayable escrow for other orders - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`, also `sdk/packages/core/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` in these `IntentGatewayV2` variants transfers the user-specified `order.inputs[i].amount` via a plain `safeTransferFrom`, then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount` (the requested amount minus only the protocol fee). If the input token charges a fee on transfer, the gateway's actual token balance increases by less than the amount credited to escrow, exactly mirroring the Taurus `BaseVault` bug where `userDetails[_account].collateral` is incremented by the requested amount rather than what was actually received.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the non-predispatch escrow path is: [1](#0-0) 
which calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then immediately does `_orders[commitment][token] += reducedInputs[i].amount` — no `balanceOf` check before/after the transfer is performed, so a fee-on-transfer token silently under-funds the escrow relative to what is recorded.

Contrast this with the corrected implementation in `evm/src/apps/IntentGatewayV2.sol`, which explicitly snapshots balances and mutates `order.inputs[i].amount` to the actually-received amount before crediting escrow: [2](#0-1) 
This fix (and the analogous predispatch-path fix using `balancesBefore`/`balancesBefore` diffing at lines 260-311) is present in `evm/src/apps/IntentGatewayV2.sol` and is exercised by dedicated fee-on-transfer tests (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, etc.): [3](#0-2) 

The `evm/tron/contracts/apps/IntentGatewayV2.sol` version (and the same pattern appears to exist in `sdk/packages/core/contracts/apps/IntentGatewayV2.sol`, which shares the identical `placeOrder` structure per its interface docs) never received this fix — it still trusts the nominal `order.inputs[i].amount` for escrow bookkeeping.

`_orders[commitment][token]` values for a given `token` are drawn against a single pooled `IERC20(token).balanceOf(address(this))` balance for the whole contract. When the escrow for one commitment is inflated beyond what was actually deposited, releasing that escrow (via `_withdraw`/`RedeemEscrow`/`RefundEscrow`, reached through `cancelOrder` or a solver `fillOrder`) transfers out more of the token than that specific order actually contributed, depleting the shared balance. Any other order using the same fee-on-transfer token as an input can then have its own (correctly-sized on paper) escrow become unpayable — `safeTransfer` will revert due to insufficient balance, or a first-mover can drain the shared pool leaving later withdrawers unable to redeem, exactly as described in the original report's Alice/Bob walk-through.

### Impact Explanation
This permanently freezes/breaks the accounting invariant that `sum(_orders[*][token])` should equal the actual token balance held. Legitimate users placing orders with fee-on-transfer tokens (or any subsequent order sharing that token) can have their escrow become unbacked, leading to reverted withdrawals or fund loss for later claimants — a concrete freezing-of-funds impact reachable via a single, unprivileged `placeOrder` transaction.

### Likelihood Explanation
Any user can call `placeOrder` with an arbitrary ERC20 token address as an input asset; no privileged role is required. The only precondition is that the chosen input token charges a transfer fee (a known, non-exotic ERC20 pattern). Because the vulnerable code path is the default (non-predispatch) escrow branch, it is trivially reachable.

### Recommendation
Apply the same balance-snapshot pattern used in `evm/src/apps/IntentGatewayV2.sol` (lines 312-329 and 260-311) to `evm/tron/contracts/apps/IntentGatewayV2.sol` and `sdk/packages/core/contracts/apps/IntentGatewayV2.sol`: read `IERC20(token).balanceOf(address(this))` before and after `safeTransferFrom`, use the delta as the actually-received amount for both the commitment hash computation and the `_orders[commitment][token]` credit, and emit `DustCollected` for any excess as done in the fixed version.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g. 1% fee) and register it as a valid input token.
2. User A calls `placeOrder` on the unpatched `IntentGatewayV2` (tron or sdk/core variant) with `inputs[0].amount = 1000` of the fee token; the gateway actually receives only 990, but `_orders[commitmentA][token]` is credited with `1000` (minus protocol fee if any).
3. User B calls `placeOrder` similarly with `inputs[0].amount = 1000`; gateway now holds `990 + 990 = 1980` tokens but total escrowed credit across both commitments is `~2000`.
4. User A cancels (same-chain) via `cancelOrder` → `withdraw`, which calls `IERC20(token).safeTransfer(beneficiary, 1000)` per the credited (inflated) escrow, draining `1000` from the shared `1980` balance, leaving only `980` for User B's `1000`-credited escrow.
5. User B's subsequent `cancelOrder`/fill-redeem call reverts on `safeTransfer` due to insufficient balance — User B's funds are permanently stuck, reproducing the original Taurus `BaseVault` Alice/Bob shortfall scenario.

Note: I was not able to fully verify the exact `placeOrder`/`withdraw` line-for-line implementation in `sdk/packages/core/contracts/apps/IntentGatewayV2.sol` within the available tool budget — only its interface/event definitions were retrieved. The vulnerability is confirmed directly against `evm/tron/contracts/apps/IntentGatewayV2.sol`; the `sdk/packages/core` variant should be checked with the same diff pattern to confirm whether it has the `evm/src` fix or the unpatched tron behavior.

### Citations

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
