### Title
Unauthenticated `CallDispatcher.dispatch()` lets anyone drain stray token/ETH balances left in the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, shared, permissionless contract used by `IntentGatewayV2.placeOrder` (predispatch swap flow) and `IntentsBase._execute` (output-call execution/dust sweep) to route intermediate token balances during order fulfillment. Like the Particle Exchange `_execBuyNftFromMarket()` bug — which verified only the *post-action* state (`ownerOf() == address(this)`) without checking whether the asset was *already present* beforehand — Hyperbridge's intents flow verifies only the dispatcher's *absolute current balance* after a call, never distinguishing funds produced by the current order's call from funds that happen to already sit in the dispatcher. Compounding this, `CallDispatcher.dispatch()` itself has no access control at all, so any leftover balance is directly, permissionlessly withdrawable by anyone.

### Finding Description
`CallDispatcher.dispatch(bytes)` is `external` with no caller restriction: [1](#0-0) 

It executes arbitrary `Call[]` instructions "as itself," moving out whatever ETH/ERC20 the contract currently holds to any `to` address the caller specifies — nothing scopes this to `IntentGatewayV2` or `HyperFungibleToken`.

The intents flows treat the dispatcher's absolute balance as ground truth rather than a delta relative to the current call:

- In `IntentGatewayV2.placeOrder`'s predispatch path, after the predispatch call, the code checks `IERC20(token).balanceOf(dispatcher) >= requiredAmount` and sweeps the *entire* balance into escrow, crediting whatever gets swept as `order.inputs[i].amount`, with no snapshot of the dispatcher's balance taken *before* the predispatch call ran: [2](#0-1) 
- In `IntentsBase._execute`, after dispatching `order.output.call`, *any* residual balance found on the dispatcher for the order's declared output tokens is swept and unconditionally emitted/treated as `DustCollected`, again without a pre-call baseline: [3](#0-2) 
- If `order.output.call` produces tokens *not* in `order.output.assets`, those balances are never swept by `_execute` at all and remain stranded on the dispatcher indefinitely.
- The tron variant of `IntentGatewayV2` has the identical unconditioned-balance pattern: [4](#0-3) 

Because the dispatcher is a long-lived singleton contract (its address is fixed configuration, `_params.dispatcher`), any stray ETH (it has a bare `receive()`) or ERC20 tokens left on it — from stranded output-call byproducts, rounding, a user directly transferring tokens to its known address, or any other integration reusing it — sit there until someone acts. Since `dispatch()` has no access control, any third party can call it directly to sweep that balance to themselves before the protocol's own sweep logic runs, exactly paralleling the original bug's core flaw: verifying "funds are present" without verifying they were legitimately produced by the current, authorized action.

### Impact Explanation
Concrete theft of funds is possible: any ETH or ERC20 balance that ends up on the shared `CallDispatcher` (dust from `_execute`'s incomplete output-token coverage, tokens sent to its public address, or timing windows around predispatch flows) can be permissionlessly drained by any caller via a direct `dispatch()` call, bypassing both `IntentGatewayV2` and `IntentsBase` entirely. This is not a self-only griefing issue — the stolen value can belong to solvers/users whose orders generated it, and to the protocol's own collected dust.

### Likelihood Explanation
The dispatcher's `receive()` and lack of any modifier on `dispatch()` make exploitation trivial and require no special privileges — any EOA can call it once any balance is observed on-chain (a single `balanceOf`/`balance` check away). Dust accumulation in `_execute` for non-enumerated output tokens is a normal byproduct of DEX/composable routing (e.g., partial swaps, referral rewards, extra tokens returned by a router), making non-zero balances a realistic and recurring occurrence rather than a contrived edge case.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to an allow-listed set of callers (e.g., an `onlyAuthorized` modifier gating `IntentGatewayV2`/`IntentsBase`/`HyperFungibleToken` instances), or make the dispatcher deploy per-call/per-order (ephemeral) rather than a shared singleton.
- In `placeOrder`'s predispatch flow and in `_execute`, snapshot the dispatcher's balance *before* executing the user/solver-supplied call and only treat the *delta* as legitimately produced funds, rather than trusting the absolute post-call balance.
- Ensure all tokens potentially produced by `order.output.call` are swept (or provide a permissioned sweep/rescue function restricted to governance) so no token type can be permanently stranded on the dispatcher.

### Proof of Concept
1. A solver's `fillOrder` executes an `order.output.call` via `CallDispatcher.dispatch` that, as a side effect of a DEX route, leaves 5 units of `TOKEN_X` on the dispatcher — a token not listed in `order.output.assets`, so `IntentsBase._execute`'s sweep loop never touches it.
2. `TOKEN_X` now sits on the publicly known `CallDispatcher` address indefinitely.
3. Any third party calls `CallDispatcher.dispatch(abi.encode([Call({to: TOKEN_X, value: 0, data: transfer(attacker, 5)})]))` directly — no authorization check prevents this — and receives the 5 `TOKEN_X` that rightfully belonged to the protocol/solver.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L39-62)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
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
