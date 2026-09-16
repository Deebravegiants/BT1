## Finding: Tron `IntentGatewayV2.placeOrder` lacks fee-on-transfer accounting present in the main EVM contract

### Title
Fee-on-transfer tokens break escrow accounting in Tron `IntentGatewayV2.placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits `_orders[commitment][token]` with the user-declared `order.inputs[i].amount` (minus protocol fee), instead of the amount the contract actually received from `safeTransferFrom`. If the escrowed token charges a transfer fee, the contract records more escrow than it actually holds.

### Finding Description
In the Tron contract, escrow crediting is based on `reducedInputs[i].amount`, which is derived purely from `order.inputs[i].amount` reduced by the protocol fee — it is never reconciled against actual token balance received: [1](#0-0) 

Specifically, for the non-predispatch path:
```
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
...
_orders[commitment][token] += reducedInputs[i].amount;
```
No balance-before/balance-after check is performed, so if `token` charges a transfer fee, the contract holds less than `reducedInputs[i].amount` while crediting the full amount to `_orders`.

This is a real regression relative to the primary EVM contract `evm/src/apps/IntentGatewayV2.sol`, which was explicitly hardened against this exact bug class. There, Phase 1 of `placeOrder` snapshots balances before/after `safeTransferFrom` and mutates `order.inputs[i].amount` to the actual amount received before computing the commitment or crediting escrow: [2](#0-1) 

The dedicated foundry test suite for the main contract even exercises this exact scenario with a `FeeOnTransferToken` mock and asserts the escrow matches actual received balance, confirming that fee-on-transfer support is an explicit protocol requirement: [3](#0-2) 

The Tron contract's `placeOrder` has no equivalent balance measurement — it inherited the pre-fix accounting logic: [4](#0-3) 

### Impact Explanation
Because `_orders[commitment][token]` is inflated beyond the actual token balance held by the contract, later redemption via `withdraw()` (called from `onAccept` for `RedeemEscrow`/`RefundEscrow`, or directly for same-chain `cancelOrder`) will attempt to transfer out `body.tokens[i].amount`, which is derived from the inflated escrow bookkeeping: [5](#0-4) 

This causes the shared token pool backing all orders on the contract to become under-collateralized: once one fee-on-transfer order's inflated claim is paid out, it is paid from tokens that legitimately belong to other users' escrowed orders, i.e., cross-order fund draining/insolvency, or later withdrawals for unrelated orders revert due to insufficient balance, permanently freezing those users' funds. This is a direct violation of the escrow's fundamental invariant that recorded balances must not exceed real balances.

### Likelihood Explanation
Any unprivileged user can reach `placeOrder` with a fee-on-transfer ERC20 as `order.inputs[i].token` in a single transaction — no special privileges are required, and the escrow mis-accounting is deterministic and reproducible on every such deposit, matching exactly the FOT bug class already fixed on the main EVM chain contract but left unpatched on Tron.

### Recommendation
Apply the same balance-based reconciliation used in `evm/src/apps/IntentGatewayV2.sol` (measure `balanceOf(address(this))` before/after each `safeTransferFrom`, and use the delta — not the requested `amount` — when computing `reducedInputs`/the commitment and crediting `_orders`) to the Tron contract's `placeOrder`, for both the predispatch and non-predispatch code paths.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with a fee-on-transfer ERC20 (e.g., 1% fee) as an allowed input token.
2. User calls `placeOrder` with `order.inputs[0].amount = 1000e18`. The contract's actual received balance is `990e18` (1% fee deducted by the token), but `_orders[commitment][token]` is credited with `1000e18` (minus protocol fee, if any) — a value the contract never actually holds.
3. Solver fills the order or the order is refunded/cancelled; `withdraw()` transfers out the inflated `_orders[commitment][token]` amount, which is `10e18` more than what this order's deposit actually contributed to the contract's balance.
4. Repeating this with multiple fee-on-transfer deposits accumulates a shortfall against the contract's real token balance, causing subsequent unrelated orders' withdrawals of the same token to revert (funds frozen) or, if paid out first, to be paid using tokens belonging to other still-pending orders (funds stolen from other users).

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-374)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
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
