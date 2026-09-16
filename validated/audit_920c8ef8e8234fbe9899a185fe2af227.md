This confirms it: `CallDispatcher` is a generic, permissionless, address-based utility contract with `dispatch(bytes)` open to `external` calls with no access control — anyone can call `dispatch` directly on the shared `_params.dispatcher` address, and its `receive()` accepts ETH from anyone [1](#0-0) . Since `dispatch` just forwards arbitrary calls the caller supplies, an attacker can donate tokens/ETH to the dispatcher and then also directly drive its `dispatch` — but more importantly, `IntentGatewayV2.placeOrder` treats whatever balance currently sits on this shared dispatcher as belonging to the current order.

### Title
Excess/pre-existing token or native balance at the shared `dispatcher` is swept into an attacker's own order in `IntentGatewayV2.placeOrder` - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder`'s predispatch branch measures how much to sweep from the shared `_params.dispatcher` by reading `IERC20(token).balanceOf(dispatcher)` / `address(dispatcher).balance` rather than tracking only the amount it just transferred there, exactly the "measure balance instead of tracked delta" antipattern from the reported `BaseAsyncSwapper` issue.

### Finding Description
In `placeOrder`, when `order.predispatch.call.length > 0`, the gateway transfers each `predispatch.assets[i].amount` to the single shared `_params.dispatcher` contract, invokes attacker-supplied `order.predispatch.call` through it, and then sweeps tokens back with:
```solidity
uint256 balance = IERC20(token).balanceOf(dispatcher);
if (balance < requiredAmount) revert InvalidInput();
transferCalls[i] = Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)});
``` [2](#0-1) 
and the equivalent for native tokens at lines 268-272. The swept amount `balance` is the *entire* current token/ETH balance held by `dispatcher`, not the amount the current caller deposited. `dispatcher` is a single shared `CallDispatcher` instance whose `dispatch` function is itself `external` and unauthenticated [3](#0-2) , and it has a public `receive()` [4](#0-3) , so any address can push tokens or ETH to it at any time, outside of any specific order's transaction. Because the sweep in `placeOrder` credits `received = balanceOf(this) - balancesBefore[i]` toward the *caller's own* order input (crediting up to `order.inputs[i].amount`, with any surplus merely emitted as `DustCollected` and left sitting in the gateway, not returned to whoever actually owned it) [5](#0-4) , any balance the dispatcher holds for *any* reason (leftover dust from a different, unrelated order's predispatch call in the same block, a donation, or funds in flight from a legitimate multi-step predispatch flow) can be claimed by the next `placeOrder` caller with a minimal `predispatch.assets[i].amount` (e.g., 1 wei) for that same token. The `dispatcher` address is not order-scoped or one-time-use — it is a persistent shared contract (`_params.dispatcher`) reused across every `placeOrder` call [6](#0-5) , so nothing prevents balance intended for one order from being swept by a different, unrelated caller's order in a subsequent (or front-run) transaction. `ReentrancyGuardTransient` only guards re-entrancy within one transaction and does not stop an attacker from monitoring the mempool and inserting their own `placeOrder` call to sweep a dispatcher balance left transiently exposed between another user's `safeTransferFrom`/`_sendValue` step and their `dispatch(order.predispatch.call)` sweep step, or any residual dust the predispatch call itself produces in a token other than the ones explicitly swept.

### Impact Explanation
An attacker can steal tokens or ETH that land on the shared `dispatcher` address that were not intended for their own order — either dust left by another order's predispatch flow, tokens mistakenly or maliciously donated to the dispatcher, or funds momentarily exposed during another party's `placeOrder` execution — by crafting a minimal predispatch order that requires only 1 wei of the target asset but sweeps and credits the dispatcher's *entire* balance to their own escrowed order input, i.e., theft of user/protocol funds. This directly parallels the External Report's "excess sellTokenBalance is stolen" class: value sitting at a shared/intermediate contract address is measured via `balanceOf` rather than tracked per-caller, and the function that performs the sweep (`placeOrder`) is fully public/unprivileged.

### Likelihood Explanation
Reachable from a single unprivileged `placeOrder` call by any address (order placement is the base, permissionless entry point of the intents flow) [7](#0-6) , requiring no privileged role, and the underlying `dispatcher` is a generic contract with an open `receive()` and unauthenticated `dispatch()` that anyone can already interact with directly [8](#0-7) , so setting up a stray balance for a victim (or discovering one) does not require any special access.

### Recommendation
Do not derive the swept amount from `balanceOf(dispatcher)`. Instead, snapshot `balanceOf(dispatcher)` immediately *before* transferring the current order's `predispatch.assets[i].amount`, and after the predispatch call sweep, only pull `balanceAfter - balanceBefore` (capped to what the predispatch call actually produced for this order), reverting if it is less than `requiredAmount`. Any genuine surplus produced by the predispatch call itself should still be tracked per-order rather than measured against the dispatcher's raw, shared balance.

### Proof of Concept
1. Some balance of token `T` ends up sitting at the shared `_params.dispatcher` address — e.g., a normal user's `placeOrder` predispatch call for `T` leaves 1000 `T` there transiently, or an unrelated party sends `T` directly to `dispatcher` (its `receive`/ERC20 transfer has no gate).
2. Attacker calls `placeOrder` with `predispatch.assets = [{token: T, amount: 1}]` and `predispatch.call` a no-op/benign call, and `order.inputs = [{token: T, amount: 1000}]`.
3. `placeOrder` transfers the attacker's 1 wei of `T` to `dispatcher`, executes the no-op predispatch call, then reads `balance = IERC20(T).balanceOf(dispatcher)` which now includes the pre-existing 1000 `T`, and sweeps the full `balance` to the gateway [9](#0-8) .
4. The swept amount is credited as `order.inputs[i].amount = received` (up to 1000, matching the attacker's declared `requiredAmount`) into the attacker's own escrow via `_orders[commitment][token]` [10](#0-9) , letting the attacker claim tokens they never contributed.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
```

**File:** evm/src/apps/IntentGatewayV2.sol (L236-236)
```text
            address dispatcher = _params.dispatcher;
```

**File:** evm/src/apps/IntentGatewayV2.sol (L268-282)
```text
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L291-368)
```text
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

        // Phase 2: Compute protocol fees and commitment from actual received amounts.
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
                if (originalAmount == 0) revert InvalidInput();
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            order.inputs = reducedInputs;
        } else {
            reducedInputs = order.inputs;
        }
        commitment = keccak256(abi.encode(order));

        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;
```
