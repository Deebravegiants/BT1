### Title
IntentGatewayV2 predispatch/output-calldata escrow credits the entire raw balance of the shared `CallDispatcher`, letting an attacker sweep other users' residual dust into their own order - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.placeOrder`'s predispatch phase, and `IntentsBase._execute`'s output-calldata phase, both credit escrow/dust by reading the *raw* `balanceOf(dispatcher)` (or `dispatcher.balance`) of the single, contract-wide `CallDispatcher` rather than tracking only the amount actually attributable to the caller's own transfer. Any tokens left sitting on the shared `CallDispatcher` — from a prior order's partially-executed predispatch/postdispatch calldata, a failed sweep, or any other in-flight interaction — get swept wholesale into whichever order happens to run next. This mirrors the PancakeBunny root cause: crediting a mint/escrow amount from an externally-influenceable aggregate balance rather than an internally tracked delta specific to the actor being credited.

### Finding Description
`placeOrder`'s predispatch branch sends the declared `predispatch.assets` to `_params.dispatcher`, executes the user-supplied `order.predispatch.call`, and then reads the dispatcher's *total* balance of each input token to decide how much to sweep into escrow: [1](#0-0) 

```
uint256 balance = IERC20(token).balanceOf(dispatcher);
if (balance < requiredAmount) revert InvalidInput();
transferCalls[i] = Call({... data: transfer(address(this), balance) ...});
balancesBefore[i] = IERC20(token).balanceOf(address(this));
```

and then measures `received = balanceOf(address(this)) - balancesBefore[i]` and credits it as `order.inputs[i].amount`, emitting any excess above `requiredAmount` as `DustCollected`: [2](#0-1) 

The `_execute` helper (used both same-chain and cross-chain, after a solver-supplied output calldata call) does the same thing for *sweeping*: it reads the dispatcher's raw balance and forwards the entire amount back into the gateway as `DustCollected`: [3](#0-2) 

`_params.dispatcher` is a single, contract-wide `CallDispatcher` instance shared by every `placeOrder`/`fillOrder` call across every order in the gateway — it is not per-order or per-caller. Because the credited amount is derived from `IERC20(token).balanceOf(dispatcher)` (or `dispatcher.balance`) at the moment of the sweep, rather than a delta strictly attributable to the current caller's own transfer into the dispatcher, any token balance that happens to be sitting on the dispatcher for any reason (a prior order's predispatch call that didn't fully consume/forward its assets, a partially-failed sweep in `_execute`, or a race where two `placeOrder`/`fillOrder` calls target the dispatcher in the same block from different EOAs) is entirely up for grabs by whichever caller's `dispatch()` sequence runs next and reads that balance. This is structurally the same bug class as PancakeBunny: the vault (`recordStake` in the codebase's own `MiniStaking` mock, and PancakeBunny's real `_calculatePerformanceFee`) credited a party based on the token's aggregate balance held by a shared contract, which an attacker could inflate immediately beforehand with an unrelated deposit, rather than tracking exactly what that specific interaction transferred in.

### Impact Explanation
If any tokens are left resident on the shared `CallDispatcher` between transactions (e.g., an order's predispatch/postdispatch calldata under-executes, a call reverts partway leaving assets stuck, or dust from a previous `_execute` sweep hasn't been fully cleared), the next caller through either `placeOrder`'s predispatch path or `_execute`'s sweep path will have that residual balance credited to their own order's escrow or forwarded as protocol dust attributable to their fill — effectively letting an attacker permanently misappropriate funds that belonged to another user's order or to the protocol's dust accounting. This is a fund-safety issue reachable by any unprivileged user simply calling `placeOrder`/`fillOrder` with a crafted predispatch/output call, matching the "concrete theft" bar for validity.

### Likelihood Explanation
Exploitability depends on there being a nonzero residual balance on the shared `CallDispatcher` at the time of the sweep. This can arise from ordinary usage (a predispatch/postdispatch call that swaps less than expected, a DEX call that leaves slippage-related leftovers, or an interrupted multi-call batch) rather than requiring a privileged actor — any user's own calldata can intentionally leave dust on the dispatcher for a follow-up transaction to claim. Because `dispatch()` calls are not scoped per-caller and the credited amount is a raw `balanceOf` read, this is a realistic and repeatable griefing/theft vector rather than a purely theoretical one, though it requires a preceding transaction (by the attacker or by chance from another user) to seed the dispatcher balance first.

### Recommendation
Do not compute escrowed/swept amounts from `IERC20(token).balanceOf(dispatcher)` / `dispatcher.balance`. Instead, track balances immediately before and after each caller's own dispatch sequence and only credit the exact delta caused by that caller's specific assets/calls (as is already partially done for `address(this)`'s own balance deltas). Where a shared `CallDispatcher` is used, snapshot its balance for the relevant token(s) *before* transferring the caller's own predispatch assets into it and only sweep `balanceOf(dispatcher) - balanceBeforeCallerDeposit`, or better, avoid relying on a shared, stateless dispatcher altogether by using a fresh, single-use dispatcher/proxy per order, or by requiring the calldata itself to push exact amounts back rather than sweeping whatever remains.

### Proof of Concept
Exact reachability (both are unprivileged, single-transaction entry points):
1. Attacker (or any user) calls `placeOrder` with a `predispatch.call` designed to leave residual `token` balance on `_params.dispatcher` after execution (e.g., a swap call that receives more than it forwards, or simply transfers extra tokens to the dispatcher as part of the calldata without them being consumed) — see `evm/src/apps/IntentGatewayV2.sol` lines 235-258.
2. In the same or a later transaction, the attacker places (or fills) a second order whose predispatch/output-call phase triggers the sweep logic at `evm/src/apps/IntentGatewayV2.sol` lines 263-311 or `evm/src/apps/intentsv2/IntentsBase.sol` lines 498-533. The sweep reads `IERC20(token).balanceOf(dispatcher)`, which now includes both the attacker's newly deposited assets *and* the residual balance left over from step 1 (which may belong to a different, unrelated order/user).
3. The full balance is transferred to `address(this)` and credited either as the attacker's own order input (`order.inputs[i].amount`) or emitted as `DustCollected` attributed to the attacker's fill, without any accounting distinguishing "funds the attacker actually deposited this call" from "funds already sitting on the shared dispatcher."

I was not able to fully verify from the index whether `evm/src/utils/CallDispatcher.sol` enforces any additional invariant (e.g., an owner-only sweep-back-to-zero at the end of every `dispatch()` call) that would fully neutralize residual balances; the file's contents were only partially retrieved. A Devin session with full repository access should confirm `CallDispatcher.dispatch()`'s exact semantics (in particular whether it can be left holding a nonzero balance after any legitimate call sequence, including reverts within the batch) before finalizing severity.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L263-282)
```text
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L289-311)
```text
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
