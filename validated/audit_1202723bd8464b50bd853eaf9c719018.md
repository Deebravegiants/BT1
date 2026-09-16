### Title
Unauthenticated `CallDispatcher.dispatch()` allows anyone to drain any token/native balance the shared singleton holds — (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, canonical, publicly documented singleton contract that `IntentGatewayV2` (via `placeOrder`'s predispatch flow and `IntentsBase._execute`) and `HyperFungibleToken`/`WrappedHyperFungibleToken` (via calldata-execution on `onAccept`) all route funds through in order to execute user- or order-creator-supplied arbitrary calldata. `CallDispatcher.dispatch()` has zero access control — any externally owned account or contract can call it directly at any time to move out whatever ETH/ERC20 balance the dispatcher currently holds.

### Finding Description
`CallDispatcher.dispatch()` is declared `external` with no caller check whatsoever: [1](#0-0) 

It accepts an arbitrary `Call[]` and executes each entry with `to.call{value: call.value}(call.data)` using the dispatcher's own balance/context. It also has a bare `receive()` that accepts native tokens from anyone: [2](#0-1) 

This is not a private, per-order or per-caller scratch contract — it is a single, deterministically-deployed shared instance whose address is publicly documented and reused across multiple unrelated protocol flows:
- `IntentGatewayV2.placeOrder`'s predispatch phase transfers the user's escrowed input assets to `dispatcher` and then calls `dispatch(order.predispatch.call)` with attacker/user-supplied calldata before sweeping the resulting balance back: [3](#0-2) 
- `IntentsBase._execute` (invoked from `fillOrder`) dispatches `order.output.call` — calldata chosen by the *order creator*, not the solver who is filling — through the same shared dispatcher, then sweeps only the token addresses explicitly listed in `order.output.assets`: [4](#0-3) 
- `HyperFungibleTokenUpgradeable.onAccept`/`send` flows mint or unlock tokens directly to the same `CallDispatcher` address so that attacker/user-supplied cross-chain `data` can spend them, per the documented pattern ("mint to the CallDispatcher so the swap can spend the tokens"): [5](#0-4) 

Because `dispatch()` has no restriction on the caller, and because the dispatcher's balance is not scoped or accounted per order/caller, any value that legitimately or transiently lands on this contract is exposed:
1. Any token that a `predispatch.call`/`output.call`/HFT `data` payload causes the dispatcher to acquire but that is **not** enumerated in `order.inputs`/`order.output.assets` (e.g., swap rewards, airdrops, refunds, unclaimed approval residue) is never swept back by the gateway's own logic, since `_execute`'s sweep only iterates over the order's declared output tokens: [6](#0-5) 
   That balance then sits permanently on the publicly-known `CallDispatcher` address, and because `dispatch()` is unauthenticated, any third party can call it directly with a `Call{to: token, data: transfer(attacker, balance)}` to steal it — the protocol itself has no privileged recovery path either, since the same permissionless function is the only way to move funds out.
2. Because `order.predispatch.call`/`order.output.call` is fully attacker/order-creator controlled and executes with the dispatcher's own balance/context (not `delegatecall`, so no storage risk, but full balance risk), a malicious order can itself invoke `CallDispatcher.dispatch()` re-entrantly (no reentrancy guard exists on `CallDispatcher` itself) to redirect funds mid-flow before the gateway's own follow-up sweep call executes.

### Impact Explanation
Funds accidentally or incidentally routed to, or left over on, a permanently deployed and publicly documented "shared infrastructure" contract can be permanently stolen by any unprivileged third party, since the only function capable of moving value out of the contract (`dispatch`) is completely open. This satisfies concrete theft / permanent freezing-adjacent conditions: value that should be recoverable by the protocol or the rightful order participant is instead immediately drainable by an unrelated attacker who simply front-runs or monitors the dispatcher's balance.

### Likelihood Explanation
The `CallDispatcher` is intentionally deployed once and shared/reused across the `IntentGatewayV2` and `HyperFungibleToken`/`WrappedHyperFungibleToken` apps (its address is documented publicly for integrators), and both apps' documentation explicitly instructs users to route bridged/escrowed funds "to the CallDispatcher" so downstream calls can spend them. Any deviation between the exact set of tokens produced by an executed call and the set of tokens explicitly swept by the calling app (`order.output.assets`/`order.inputs`) — which is easy to trigger with reward-bearing DeFi calls, airdrops, or excess approvals in solver/user-supplied calldata — leaves an immediately and permanently exploitable balance on a contract with no owner check on withdrawal.

### Recommendation
Add an access-control check to `CallDispatcher.dispatch()` restricting the caller to a registered/authorized invoker (e.g., the specific `IntentGatewayV2`/`HyperFungibleToken` instance that funded it), or make the dispatcher stateless per-call (e.g., deploy an ephemeral dispatcher per call via `CREATE2`/minimal proxy that self-destructs or cannot retain balance across calls) so no value can ever persist on a permissionlessly-callable shared contract. Additionally, in `_execute` and the predispatch sweep, sweep by "delta observed during this call" for the complete list of tokens touched, and provide a privileged/owner-gated recovery path for any token not anticipated by the order's declared asset list.

### Proof of Concept
1. A user/relayer routes funds to the `CallDispatcher` singleton as documented (e.g., minting HFT tokens to `to: CALL_DISPATCHER`, or an order's `predispatch`/`output` calldata that produces a token not declared in the order's asset list, e.g. a farming/reward token acquired mid-swap).
2. Because `_execute`'s sweep only iterates `order.output.assets` (`evm/src/apps/intentsv2/IntentsBase.sol:507-533`), that extra token balance is left sitting on the `CallDispatcher` contract after the transaction completes.
3. Any attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: rewardToken, value: 0, data: transfer(attacker, IERC20(rewardToken).balanceOf(dispatcher))})]))` directly — there is no check preventing this, since `dispatch()` (`evm/src/utils/CallDispatcher.sol:44-62`) has no caller restriction — and receives the stranded balance.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-62)
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
        }
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-290)
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({from: message.from, to: beneficiary, source: string(request.source), amount: message.amount});
    }
```
