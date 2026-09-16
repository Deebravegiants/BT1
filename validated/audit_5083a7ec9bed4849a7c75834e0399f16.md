### Title
Missing reentrancy guard and inconsistent Checks-Effects-Interaction ordering in the Tron `IntentGatewayV2` allows an order to be both cancelled and filled - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of the intent gateway, `evm/tron/contracts/apps/IntentGatewayV2.sol`, duplicates the same `placeOrder`/`cancelOrder`/`fillOrder`/`withdraw` state machine as the hardened EVM contract (`evm/src/apps/IntentGatewayV2.sol`), but it does not carry the same protections. The main EVM `cancelOrder` is guarded with `nonReentrant` [1](#0-0) , and `IntrinsicIntents._fillSameChain`/`ExtrinsicIntents._fillCrossChain` were explicitly hardened to set `_filled[commitment]` before any external token transfer, exactly to close a checks-effects-interaction gap of this class (confirmed by `IntrinsicIntentsReentrancyTest.sol`) [2](#0-1) . The Tron `cancelOrder`, however, has no `nonReentrant` modifier and the contract imports no `ReentrancyGuard` at all [3](#0-2) .

### Finding Description
`IntentGatewayV2.cancelOrder` on Tron checks `_filled[commitment]` and then, for the same-chain branch, immediately calls `withdraw(body, true)`, which performs external `IERC20.safeTransferFrom`/native transfers to refund escrow [4](#0-3) . `placeOrder` similarly performs multiple external calls — `safeTransferFrom`, native `.call{value:}`, and `ICallDispatcher(dispatcher).dispatch(...)` — while escrow bookkeeping (`_orders[commitment][token] += ...`) is updated interleaved with those external calls rather than fully before them [5](#0-4) .

Because none of `placeOrder`, `cancelOrder`, or the fill path in this file carry a reentrancy guard, and because ERC-20 tokens used as order inputs/outputs can be ERC-777-style tokens (or any token with transfer hooks/callbacks), a token used in an order can re-enter the gateway during any of these external calls. Concretely: a malicious order `user`/beneficiary token can, during the `safeTransferFrom`/native transfer that `cancelOrder`'s `withdraw` performs, re-enter `fillOrder` (or another order's `cancelOrder`) before `_filled[commitment]` is durably observed as changed by other call frames, producing exactly the reported bug class — an order simultaneously "cancelled" and "filled/matched" from the perspective of different call contexts, since none of the state transitions here are atomically fenced against reentrancy the way the hardened EVM `src/apps/IntentGatewayV2.sol` + `IntrinsicIntents.sol` were fixed to be.

This mirrors the referenced Sherlock report precisely: `matchOrder()`/`buyPosition()` there run external transfers before finalizing order state, letting a reentrant `cancelOrder()` race the fill. The Tron gateway reproduces the same missing-CEI/missing-guard pattern that the EVM gateway's audit trail (`IntrinsicIntentsReentrancyTest.sol`, the `nonReentrant` modifier on `cancelOrder`) shows was deliberately fixed elsewhere in this codebase but was not carried over to the Tron implementation.

### Impact Explanation
An attacker able to make an order's input/output token a callback-capable (ERC-777-like) or malicious token can reenter the gateway mid-transfer. Depending on the exact reentrant sequence this can: (a) cause escrow to be released twice for the same commitment (double-spend of escrowed funds), since `_orders[commitment][token]` bookkeeping and the transfer are not strictly separated with a completed state update guarding against re-entry, or (b) cause an order to be filled and cancelled in the same block, letting the solver or the user extract funds intended for the other party. Given this contract handles user-escrowed ERC-20/native funds across chains, a successful reentrant race constitutes theft or double-release of escrowed funds — a High severity, not merely a UI-cosmetic issue as the original report characterized for the audited protocol, because here it directly gates fund custody.

### Likelihood Explanation
Requires an order to include a token with reentrant transfer hooks (ERC-777, or any ERC-20 with `transferFrom`/`transfer` callbacks such as tokens with `beforeTokenTransfer` hooks controllable by the attacker, or a malicious `beneficiary` contract for native-token outputs). Since orders specify arbitrary `TokenInfo.token` addresses and beneficiaries, an attacker fully controls this precondition when placing/filling their own order, making exploitation straightforward once such a token is used as an input, output, or fee token. The absence of any `nonReentrant` guard on this file (unlike the sibling `evm/src/apps/IntentGatewayV2.sol`) means there is no defense-in-depth even if the per-function CEI ordering were otherwise believed sufficient.

### Recommendation
Add a `ReentrancyGuard` (`nonReentrant`) to `placeOrder`, `cancelOrder`, `fillOrder`, and `withdraw` in `evm/tron/contracts/apps/IntentGatewayV2.sol`, matching `evm/src/apps/IntentGatewayV2.sol`. Additionally, audit and reorder all external calls so that `_filled[commitment]` and `_orders[commitment][token]` state is fully finalized before any external token transfer or `ICallDispatcher` dispatch, mirroring the CEI fix already applied and tested in `IntrinsicIntents._fillSameChain`/`ExtrinsicIntents._fillCrossChain`.

### Proof of Concept
1. Attacker deploys a malicious ERC-777-like token `T` implementing `transferFrom` with a `tokensToSend`/receive hook.
2. Attacker places a same-chain order via `placeOrder` using `T` as an input token, escrowing funds into `_orders[commitment][T]` [6](#0-5) .
3. Attacker calls `cancelOrder`, which reaches `withdraw(body, true)` and issues `IERC20(T).safeTransferFrom`/transfer to refund escrow [4](#0-3) .
4. During that transfer's hook callback, since there is no `nonReentrant` guard, the attacker's token contract re-enters `fillOrder` (or `cancelOrder` for a second commitment sharing escrow logic) before the outer call finishes, causing overlapping state transitions on the same commitment/escrow bookkeeping.
5. Result: order state ends up inconsistent — filled and cancelled/refunded concurrently — potentially double-releasing escrowed funds, unlike the guarded EVM counterpart which reverts such reentrant attempts (as demonstrated by `IntrinsicIntentsReentrancyTest.testReentrancy_FeeTheft`/`testReentrancy_EscrowTheft_MultiOutput`) [7](#0-6) .

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L505-509)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
        bytes32 commitment = keccak256(abi.encode(order));

        if (_filled[commitment] != address(0)) revert Filled();

```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L37-49)
```text
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
 */
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L224-280)
```text
    function testReentrancy_FeeTheft() public {
        // ── 1. Place a same-chain order (input=USDC, output=ETH, fees=DAI) ───

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: INPUT_USDC});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(0), amount: OUTPUT_ETH});

        Order memory order = _sameChainOrder(inputs, outputAssets, TX_FEES);

        vm.startPrank(attacker);
        usdc.approve(address(intentGateway), INPUT_USDC);
        dai.approve(address(intentGateway), TX_FEES);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Reconstruct the stamped order for commitment computation.
        order.user = bytes32(uint256(uint160(attacker)));
        order.source = host.host();
        order.nonce = 0;

        bytes32 commitment = keccak256(abi.encode(order));

        // Sanity: confirm fees are escrowed.
        assertEq(intentGateway._orders(commitment, TRANSACTION_FEES), TX_FEES);

        // ── 2. Arm the malicious beneficiary ─────────────────────────────────
        //
        // The reentrant FillOptions passes amount=0 so the re-entered loop's
        // `remaining == 0 || solverAmount == 0` branch is taken — but this
        // code path is never reached because _filled[commitment] is already set.

        TokenInfo[] memory reentrantOutputs = new TokenInfo[](1);
        reentrantOutputs[0] = TokenInfo({token: bytes32(0), amount: 0});

        maliciousBeneficiary.arm(
            order, FillOptions({relayerFee: 0, nativeDispatchFee: 0, validUntil: 0, outputs: reentrantOutputs})
        );

        // ── 3. Fill attempt reverts — reentrancy is blocked ──────────────────

        vm.expectRevert(ERR_INSUFFICIENT_NATIVE);
        vm.prank(legitimateSolver);
        intentGateway.fillOrder{value: OUTPUT_ETH}(
            order, FillOptions({relayerFee: 0, nativeDispatchFee: 0, validUntil: 0, outputs: outputAssets})
        );

        // ── 4. State is completely rolled back ───────────────────────────────

        assertEq(
            intentGateway._orders(commitment, TRANSACTION_FEES), TX_FEES, "fees must still be escrowed after revert"
        );
        assertEq(intentGateway._filled(commitment), address(0), "order must not be marked filled after revert");
        assertEq(dai.balanceOf(address(maliciousBeneficiary)), 0, "malicious beneficiary must not receive stolen fees");
        assertEq(usdc.balanceOf(legitimateSolver), 0, "solver must not have received any escrow");
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-469)
```text
        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

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

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-539)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
```
