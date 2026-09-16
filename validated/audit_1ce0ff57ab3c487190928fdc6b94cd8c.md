## Analog Confirmed: Shared CallDispatcher Executes Arbitrary Calldata in a Persistent Identity Whose Residual Approvals Any Caller Can Exploit

### Title
Unbounded, persistent token approvals granted through `CallDispatcher.dispatch()` let an unprivileged sender steal any token balance later routed through the same shared dispatcher - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
The CVE-2021-21379 bug class is a "confused deputy" / privilege-leak: content injected by an unprivileged caller executes in the persistent, shared execution context of a higher-trust actor, so effects that context leaves behind belong to that shared identity, not the caller who requested them. `CallDispatcher` reproduces this exact pattern in Hyperbridge's EVM apps: it is one singleton contract shared by every `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` deployment on a chain, and it blindly executes attacker-supplied `Call[]` arrays `to.call{value}(data)` from its own persistent address [1](#0-0) . Any unprivileged token bridger can use the `data` field of `send()` to make the dispatcher `approve()` an attacker-chosen spender for any ERC20, and that approval survives indefinitely in the dispatcher's own storage/allowance state, because `CallDispatcher` is never redeployed or reset between messages.

### Finding Description
`HyperFungibleToken.onAccept` and `WrappedHyperFungibleToken.onAccept` mint/unlock tokens to a caller-chosen `to` address and then forward caller-controlled `data` straight to the shared `CallDispatcher`: [2](#0-1) 

The dispatcher itself imposes no restriction on the target or calldata of each `Call`, and performs no cleanup after execution: [1](#0-0) 

The documented usage pattern explicitly instructs integrators to set `to` to the `CallDispatcher` address so that bridged tokens land there before composed calls run, and separately warns that "Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution" [3](#0-2)  — this is only a documentation-level mitigation for well-behaved integrators; it does nothing to stop a malicious message from granting itself an allowance over the dispatcher's *future* balances.

The same dispatcher and pattern are reused by `IntentGatewayV2`'s predispatch/postdispatch calldata, which also transfers assets to the shared dispatcher and executes attacker/solver-influenced `Call[]` arrays there [4](#0-3) [5](#0-4) .

Because `CallDispatcher` is one persistent contract instance servicing every message from every user of every app that points at it, an attacker's own cross-chain message can plant a call `token.approve(attacker, type(uint256).max)` executed by the dispatcher. This grants the attacker a standing ERC20 allowance over whatever balance of that token the dispatcher holds — now or in the future — regardless of which unrelated message or user later causes tokens to sit at that address (e.g., a legitimate transfer-and-swap message with `to = CallDispatcher`, or any postdispatch dust/timing gap in IntentGatewayV2).

### Impact Explanation
Any subsequent legitimate token balance parked at the `CallDispatcher` (by design, for composable transfer-and-swap / transfer-and-stake flows, or as dust) becomes stealable by the earlier attacker via `transferFrom`. This is concrete theft of funds reachable purely from a single unprivileged cross-chain `send()`/order submission — no governance, relayer, or admin compromise required — and the loss is not bounded to the attacker's own message: it exposes every other user who routes the same token through the dispatcher afterward.

### Likelihood Explanation
High. `send()`'s `data` field and `IntentGatewayV2`'s `predispatch`/`postdispatch` `call` fields are fully attacker-controlled and require no privilege beyond being a normal token bridger or order submitter. The dispatcher's persistence and multi-tenant sharing across the whole app are inherent to its design, so the standing-approval window exists for the dispatcher's entire operational lifetime, not a single transaction.

### Recommendation
- Make `CallDispatcher` non-persistent per call (e.g., deploy an ephemeral proxy/clone per dispatch via `CREATE2`/minimal proxy, or execute through a transient account) so no approval or balance can outlive a single dispatch.
- Alternatively, have the dispatcher explicitly revoke (`approve(target, 0)`) any approval it granted within the same `dispatch()` call after use, and sweep any residual balance back to `msg.sender`/caller before returning, rather than relying on integrator discipline.
- Add an on-chain check rejecting `approve`/`increaseAllowance`-style selectors to arbitrary spenders from within `dispatch()`, or restrict callable targets/selectors via an allowlist.

### Proof of Concept
1. Attacker calls `HyperFungibleToken.send()` (or `WrappedHyperFungibleToken.send()`) with `params.dest` = victim chain, `params.to` = the `CallDispatcher` address on that chain, and `params.data` = `abi.encode([Call({to: TARGET_ERC20, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)})])`.
2. Relayer delivers the message; `onAccept` mints/unlocks tokens to the dispatcher and forwards `data`, so `CallDispatcher.dispatch` executes `TARGET_ERC20.approve(attacker, max)` from the dispatcher's own address [1](#0-0) .
3. At any later point, any other user's transfer-and-swap message (or IntentGatewayV2 predispatch/postdispatch flow) sends `TARGET_ERC20` to the same `CallDispatcher` address as an intermediate step [3](#0-2) .
4. Attacker calls `TARGET_ERC20.transferFrom(CallDispatcher, attacker, balance)` directly, draining the tokens using the standing allowance from step 1 before (or instead of) the intended composed calls consume them.

### Citations

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-333)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L86-96)
```text
## Calldata Execution

Both contracts support optional calldata execution on the destination chain via the `CallDispatcher`. By passing a non-empty `data` field in `SendParams`, the sender can trigger arbitrary contract calls on the destination chain immediately after tokens are minted or unlocked. This enables composable cross-chain workflows like transfer-and-swap (e.g., bridge USDC then swap to WETH via UniswapV2), transfer-and-stake, or transfer-and-deposit into a lending protocol — all in a single cross-chain operation.

The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.
```

**File:** evm/src/apps/IntentGatewayV2.sol (L241-290)
```text
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
