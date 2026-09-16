### Title
`CallDispatcher.dispatch()` has no access control, letting anyone drain assets that are momentarily or residually held by the shared dispatcher used by `IntentGatewayV2` (and `HyperFungibleToken`) - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, shared, unowned helper contract used by `IntentGatewayV2` (and referenced by the Hyper Fungible Token flow) to execute arbitrary attacker/solver-supplied `Call[]` batches during predispatch/postdispatch order execution. Its only entrypoint, `dispatch(bytes memory encoded)`, has no caller restriction whatsoever.

### Finding Description
`CallDispatcher.dispatch()` decodes a `Call[]` array and blindly performs `to.call{value: call.value}(call.data)` for each entry, with no `onlyOwner`/`onlyGateway`/`onlyHost` style guard: [1](#0-0) 

`IntentGatewayV2` treats this contract as its execution sandbox: it transfers the user's predispatch assets (native ETH or ERC20) to the dispatcher **first**, then separately calls `dispatch()` to run the swap calldata, and only in a following, distinct call sweeps the resulting balance back to the gateway: [2](#0-1) 

The same pattern is used on the output/postdispatch side in `IntentsBase._execute()`: [3](#0-2) 

Because `dispatch()` is `external` with no access modifier, and `CallDispatcher` is a shared, persistent contract instance (`address dispatcher = _params.dispatcher;`), any funds sitting on that contract's balance are reachable by an arbitrary caller supplying their own `Call[]` targeting any contract (subject only to the `NotContract` extcodesize check). This is structurally identical to the reported `FlashLoanLiquidate.JOJOFlashLoan()` issue: an unauthenticated function that triggers `to.call(data)` and can be pointed at assets the contract happens to be holding.

The intended flow relies on all three steps (fund transfer → `dispatch(predispatch.call)` → sweep `dispatch(transferCalls)`) executing atomically inside one `placeOrder`/`fillOrder` transaction, so a naive reading suggests no exploitable window exists purely from mempool front-running within that single transaction. However, the root cause remains a genuine access-control gap on a function whose entire purpose is to move value on behalf of the protocol:
- The dispatcher's `receive() external payable` accepts arbitrary ETH, and its balance (from stray sends, protocol dust that fails to be fully swept for whatever token, or any other integration that stages assets there, such as the Hyper Fungible Token pattern that documents minting tokens directly `to` the `CallDispatcher` address before a swap step) is fully drainable by any unrelated address at any time, not only the `IntentGatewayV2`/token contract that is supposed to own that flow.
- Any partial failure, upgrade, or future integration that stages assets on the dispatcher across more than one transaction turns this into a directly exploitable theft primitive, since nothing in `CallDispatcher` enforces that only the staging contract (or the same transaction) may call `dispatch()`.

### Impact Explanation
If assets are held by `CallDispatcher` outside of the fully atomic happy-path (dust, a partially-swept token, native ETH sent to the contract, or tokens staged there by another integration such as `HyperFungibleToken`'s documented "mint to `CallDispatcher`" pattern), any address can call `dispatch()` directly with a `Call[]` that routes those assets to itself. This is unauthorized-fund-theft-class impact — it is the same bug class validated as Medium in the source report (assets held by a contract with an unrestricted arbitrary-call dispatch function can be stolen).

### Likelihood Explanation
Likelihood depends on how reliably the dispatcher balance returns to exactly zero after every code path (predispatch, postdispatch, fee-on-transfer tokens, reverts mid-way, and any external integrations like `HyperFungibleToken` that stage funds there across separate calls). Given `CallDispatcher` is a bare utility contract with no restriction and is reused across many callers/integrations, the risk is that any future or edge-case flow that leaves a non-zero balance (even transiently, or due to a revert leaving partial state) is instantly and permanently exploitable by anyone monitoring the dispatcher's balance — a routine MEV/bot pattern.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only the contract(s) authorized to use it (e.g., an immutable `owner`/`caller` set at construction time, or a per-deployment dispatcher scoped to a single gateway with an `onlyGateway` modifier), rather than a shared, permissionless singleton. Alternatively, ensure the dispatcher never holds a non-zero balance outside of a single atomic call by making the fund-in, dispatch, and sweep-out steps enforced within one guarded function rather than three independent public calls on a stateless dispatcher.

### Proof of Concept
Conceptual PoC (cannot be fully substantiated without confirming a concrete cross-transaction balance-residue path from the available index, see caveat below):
1. Monitor `CallDispatcher`'s ETH/ERC20 balances (the address referenced by `IntentGatewayV2.params().dispatcher`).
2. Whenever a non-zero balance is observed (e.g., due to a reverted/interrupted flow, dust not fully swept, or an external integration such as `HyperFungibleToken` staging minted tokens on the dispatcher before its own swap step runs), call `CallDispatcher.dispatch(encoded)` directly with a `Call[]` that transfers the token/ETH balance to attacker-controlled address.
3. Since `dispatch()` performs no caller check, this call succeeds and the funds are stolen from the shared dispatcher.

Caveat: I was unable to fully verify, within the available indexed contents, a concrete step-by-step transaction sequence in which `HyperFungibleToken`'s mint-to-`CallDispatcher` step and its subsequent `dispatch()` call are not executed atomically in the same transaction (the file `sdk/packages/core/contracts/apps/HyperFungibleToken.sol` grep matched many lines but I could not read its full body before running out of iterations). If mint and dispatch are always performed atomically in a single external call with no way to interleave a third-party call, the exploitable window in the current call sites may be limited to residual dust/edge cases rather than a routinely reachable full-order-value theft. I recommend a Devin session with full file access to confirm whether any call site separates the "fund the dispatcher" and "invoke dispatch" steps into different transactions or externally-triggerable steps, which would make this Medium-severity finding concretely exploitable at full scale rather than only on dust/edge-case residues.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-60)
```text
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-289)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-545)
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

        if (sweepCount > 0) {
            Call[] memory finalCalls = new Call[](sweepCount);
            for (uint256 i; i < sweepCount;) {
                finalCalls[i] = sweepCalls[i];
                unchecked {
                    ++i;
                }
            }
            ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls));
        }
    }
```
