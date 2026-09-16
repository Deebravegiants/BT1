### Title
Intent escrow can be credited without any tokens actually arriving, due to unchecked ERC20 `transfer` return values in the Tron `IntentGatewayV2` predispatch/sweep path - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Gym Network exploit stemmed from a "lack of caller verification" that let a caller increase an internal balance without ever making a real payment. `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder` has an analogous flaw in its predispatch/sweep flow: the escrow ledger `_orders[commitment][token]` is credited based on a *pre-check* of the `CallDispatcher`'s balance, and the actual token movement back to the gateway is performed through `CallDispatcher.dispatch`, which only checks that the low-level `.call` did not revert — it never checks the boolean return value of `IERC20.transfer`. A token whose `transfer` silently returns `false` on failure (rather than reverting) lets the sweep "succeed" while no tokens actually move to the gateway, yet the escrow accounting has already been incremented.

### Finding Description
In the predispatch branch of `placeOrder`: [1](#0-0) 

the loop computes `balance = IERC20(token).balanceOf(dispatcher)`, checks `balance >= requiredAmount`, builds a `transferCalls[i]` entry that calls `IERC20.transfer(address(this), balance)` on the dispatcher's behalf, and **immediately** credits escrow:
```solidity
_orders[commitment][token] += reducedInputs[i].amount;
```
The actual transfer only happens afterward, via:
```solidity
ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

`CallDispatcher.dispatch` executes each call and only reverts if the low-level call itself reverts: [2](#0-1) 
```solidity
(bool success, bytes memory result) = to.call{value: call.value}(call.data);
if (!success) revert CallFailed(to, result);
```
It never decodes/checks the boolean return of `IERC20.transfer`. Because the call target is invoked via raw `IERC20.transfer.selector` rather than `SafeERC20.safeTransfer`, a non-reverting-on-failure ERC20 (a common real-world token pattern, returns `false` instead of reverting) makes `to.call(...)` return `success == true` with an encoded `false` payload, which `dispatch` treats as success.

Consequently, escrow can be permanently credited for `reducedInputs[i].amount` while zero tokens actually reach `IntentGatewayV2`. This is structurally the same "credit an internal balance without receiving real payment" root cause as the Gym Network bug, just realized through an unchecked ERC20 return value instead of a missing caller check.

By contrast, the primary EVM implementation (`evm/src/apps/IntentGatewayV2.sol`) closes this gap by re-measuring the gateway's own balance before and after the sweep and crediting escrow only with the *actually observed* delta: [3](#0-2) 
The Tron contract lacks this post-sweep balance verification.

### Impact Explanation
Once escrow (`_orders[commitment][token]`) is credited without backing tokens, a solver can `fillOrder`/trigger `withdraw`, and the contract will attempt to pay out real tokens (from its actual, unrelated balance — funds belonging to other users' orders) against this phantom escrow entry: [4](#0-3) 
This lets an attacker drain tokens belonging to legitimately-escrowed orders using a crafted order whose input token has non-reverting-failure `transfer` semantics — an unbacked-mint-style theft of escrowed intent funds, directly reachable from a single `placeOrder` transaction.

### Likelihood Explanation
Requires the attacker to choose an input token for their `Order.inputs` whose `transfer()` returns `false` on failure instead of reverting (a known, non-trivial-but-common ERC20 non-compliance pattern), and to arrange the predispatch call/dispatcher balance so the pre-check `balance >= requiredAmount` passes while the eventual `transfer` to the gateway fails or under-delivers. This is achievable by the order placer since they fully control `order.predispatch.call` and `order.inputs`.

### Recommendation
- Use `SafeERC20.safeTransfer`/`safeTransferFrom` (or explicitly check the boolean return) inside `CallDispatcher.dispatch` for ERC20 transfer calls, or
- Mirror the main EVM contract's fix: measure `IERC20(token).balanceOf(address(this))` before and after the sweep dispatch and credit escrow only with the actually-received delta, never with the nominal `reducedInputs[i].amount`.

### Proof of Concept
1. Attacker deploys/uses an ERC20 token `EvilToken` whose `transfer` returns `false` on failure without reverting (e.g., insufficient allowance/paused state check that returns false).
2. Attacker crafts an `Order` with `predispatch.call`/`predispatch.assets` that transiently satisfies `IERC20(EvilToken).balanceOf(dispatcher) >= requiredAmount` (e.g., a self-controlled predispatch call that deposits just enough into the dispatcher, but the dispatcher's subsequent `transfer` to the gateway is made to fail-return-false, e.g. via a blacklist/pause flag flipped by a reentrant call within the same predispatch execution or via a token designed to return false on transfers to specific contracts).
3. `placeOrder` proceeds: `_orders[commitment][EvilToken] += reducedInputs[i].amount` executes, then `ICallDispatcher(dispatcher).dispatch(transferCalls)` runs `EvilToken.transfer(address(this), balance)`, which returns `false` but does not revert, so `dispatch` does not revert.
4. `IntentGatewayV2` now holds an escrow entry for `EvilToken` with no corresponding token balance.
5. Attacker (or a colluding solver) fills the order or otherwise triggers `withdraw`, and the payout for this phantom escrow is serviced from the pool of real tokens held for other users' genuine `EvilToken`-denominated escrows (or from the contract's fee-token balance if `token.call` similarly returns false without reverting on `withdraw`'s payout, causing accounting drift), resulting in theft/fund freezing for legitimate order owners.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-449)
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

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
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

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L260-306)
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
```
