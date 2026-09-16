Confirmed: `CallDispatcher` is a single, shared, permissionless singleton contract deployed once and referenced via `_params.dispatcher` by the `IntentGatewayV2` proxy on that chain [1](#0-0) . It executes arbitrary calls forwarded by *anyone* who can reach `dispatch()` — including any `placeOrder` caller's `order.predispatch.call` — and has no access control, no per-caller scoping, and a `receive()` that accepts stray ETH [2](#0-1) .

### Title
Balance-based sweep from a shared, unscoped `CallDispatcher` lets a predispatch order steal residual/foreign token balances into escrow - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder`'s predispatch path measures how much of each input token to escrow by reading the *entire current* `balanceOf(dispatcher)` rather than a value scoped to the specific order/call, exactly the same "trust the live balance instead of a tracked delta" pattern that let the OLPC attacker inflate a Pancake pair's reserves and drain LABUBU. Because `dispatcher` (`CallDispatcher`) is one shared, stateless, permissionless singleton used by every order on the chain, any tokens that land on it — from another user's in-flight predispatch call, an unswept previous order, a stuck approval-based pull, or an attacker's own crafted predispatch call that yanks tokens from a third-party contract that has approved the dispatcher — get folded into the caller's escrow via the "sweep full balance" logic.

### Finding Description
In `placeOrder`, when `order.predispatch.call.length > 0`, the gateway:
1. Transfers `order.predispatch.assets[i].amount` of each token to `dispatcher`, then calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` with **attacker-supplied `Call[]` data** [3](#0-2) .
2. Snapshots `balancesBefore[i] = IERC20(token).balanceOf(address(this))`, then builds a sweep call that transfers **`balance = IERC20(token).balanceOf(dispatcher)`** (the dispatcher's *full* live balance, not the amount actually delivered by the predispatch call) from `dispatcher` to the gateway [4](#0-3) .
3. Computes `received = balanceOf(address(this)) - balancesBefore[i]` and sets `order.inputs[i].amount = received` (capped to the declared amount, excess treated as "dust") [5](#0-4) .

Because `dispatch()` on `CallDispatcher` performs an arbitrary external `call{value: call.value}(call.data)` to any contract with a positive `extcodesize`, and imposes no restriction on what the call does or who benefits [6](#0-5) , an attacker's `order.predispatch.call` can direct `CallDispatcher` (acting as `msg.sender`) to pull tokens from any third party that has ever approved `CallDispatcher` (e.g., a leftover approval from a prior order's predispatch flow, or any other protocol that mistakenly grants the shared dispatcher an allowance), or simply race a legitimate user's own predispatch transaction so both land in the same block/mempool window and the attacker's sweep captures tokens intended for someone else's order. Since the sweep reads `IERC20(token).balanceOf(dispatcher)` unconditionally rather than tracking only the exact amount the current predispatch call produced, the escrowed `order.inputs[i].amount` (and thus the value backing the ISMP-dispatched or same-chain-filled order) can be inflated using funds the placing user never contributed — mirroring how OLPC's bridge wrapper trusted the pair's live token balance (inflated via sync/skim by a malicious hook) instead of a per-transaction accounted amount.

### Impact Explanation
An attacker can escrow (and subsequently redeem via `fillOrder`, cross-chain delivery, or cancellation/timeout) tokens that were never actually deposited by them, effectively minting value out of residual or third-party balances sitting on the shared `CallDispatcher`. This is concrete theft of funds routed through Hyperbridge's own token-bridging/intents primitive, satisfying the "concrete theft" bar for Medium/High severity in a permissionless-dispatch context reachable by any `placeOrder` caller.

### Likelihood Explanation
Reachability requires only a single `placeOrder` call with `predispatch.call` populated — a wholly unprivileged transaction path already exercised in the test suite (e.g., `testPlaceOrder_FeeOnTransferToken_Predispatch`) [7](#0-6) . The precondition (dispatcher holding attacker-influenceable balance, whether via a dangling approval, unswept dust, or timing against a concurrent legitimate predispatch) is plausible given `CallDispatcher` is a stateless singleton with no per-order isolation, but exploitability in practice depends on whether any real integration ever leaves an approval or balance on the shared dispatcher — this is the part I could not fully verify from the indexed code (no evidence of persistent approvals to `CallDispatcher` was found, and same-block/mempool ordering assumptions add some friction).

### Recommendation
Scope the sweep to the amount actually produced by the predispatch call instead of the dispatcher's absolute balance: snapshot `balanceOf(dispatcher)` immediately *before* dispatching `order.predispatch.call` and sweep only the delta (`balanceAfterPredispatch - balanceBeforePredispatch`), never the dispatcher's full standing balance. Additionally, consider deploying a fresh, single-use dispatcher (or using `CREATE2`-ephemeral proxies) per order, or asserting `balanceOf(dispatcher) == 0` for each input token both before and after the sweep so no residual value can ever be attributed to an order that didn't produce it.

### Proof of Concept
Conceptual PoC (pattern matches the OLPC analog):
1. Attacker (or accomplice) leaves/creates a standing ERC20 allowance from a victim contract (or a prior stuck order) to `CallDispatcher`.
2. Attacker calls `placeOrder` with `order.predispatch.call` encoding a `Call` that makes `CallDispatcher` execute `token.transferFrom(victim, dispatcher, X)` (or simply relies on dust/timing so `balanceOf(dispatcher)` already reflects unrelated funds) — no attacker-owned tokens need be transferred in for this `X`.
3. The gateway's sweep step reads `balance = IERC20(token).balanceOf(dispatcher)` including `X`, transfers it all to the gateway, and computes `received = X`, setting `order.inputs[i].amount = X` [8](#0-7) .
4. Attacker's order is now escrowed with `X` tokens they never contributed, which they can redeem via cancellation/timeout or use as backing for a fraudulent fill, without ever having supplied the underlying value — the direct analog of OLPC's manipulated-reserve, `amountIn = 0` release of LABUBU.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L25-62)
```text
contract CallDispatcher is ICallDispatcher {
    /**
     * @dev error thrown when the target is not a contract.
     */
    error NotContract(address target);

    /**
     * @dev error thrown when a call fails.
     */
    error CallFailed(address target, bytes result);

    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-258)
```text
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
```

**File:** evm/src/apps/IntentGatewayV2.sol (L260-311)
```text
            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

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

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2625-2686)
```text
    function testPlaceOrder_FeeOnTransferToken_Predispatch() public {
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% transfer fee
        fot.mint(user, 10000 * 1e18);

        uint256 predispatchAmount = 1000 * 1e18;
        // After transferring to dispatcher: 1% fee = dispatcher receives 990
        uint256 dispatcherReceived = predispatchAmount - (predispatchAmount * 100) / 10000;
        // After dispatcher transfers to gateway: another 1% fee = gateway receives ~980.1
        uint256 gatewayReceived = dispatcherReceived - (dispatcherReceived * 100) / 10000;

        // Predispatch: send FOT to dispatcher, the "call" is a no-op (empty calls array)
        TokenInfo[] memory predispatchAssets = new TokenInfo[](1);
        predispatchAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: predispatchAmount});

        // The predispatch call is an empty Call[] dispatch (no-op, tokens just sit on dispatcher)
        Call[] memory emptyCalls = new Call[](0);
        bytes memory predispatchCall = abi.encode(emptyCalls);

        // Inputs: expect the FOT that lands on dispatcher after predispatch
        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: dispatcherReceived});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 500 * 1e18});

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
            predispatch: DispatchInfo({assets: predispatchAssets, call: predispatchCall}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        fot.approve(address(intentGateway), predispatchAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Gateway should hold only what it actually received (double fee-on-transfer)
        assertEq(fot.balanceOf(address(intentGateway)), gatewayReceived, "Gateway should hold double-taxed amount");

        // Reconstruct commitment
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = gatewayReceived; // mutated to actual received
        bytes32 commitment = keccak256(abi.encode(order));

        assertEq(
            intentGateway._orders(commitment, address(fot)),
            gatewayReceived,
            "Escrow should match actual received after double transfer fee"
        );
    }
```
