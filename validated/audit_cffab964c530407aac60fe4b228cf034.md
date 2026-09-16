## Title
`CallDispatcher.dispatch()` has no access control, letting anyone drain any token/ETH balance the shared dispatcher happens to hold — ([File: evm/src/utils/CallDispatcher.sol])

## Summary
`CallDispatcher` is a single, shared, permissionless "untrusted call executor" reused by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` (deployed once per chain via CREATE2). Its `dispatch()` function executes an attacker-supplied `Call[]` with the `CallDispatcher`'s own identity and balance, and it has **no caller restriction whatsoever** — not `onlyHost`, not an allow-list of the apps that are supposed to use it, nothing. Any address, including an unprivileged intent solver or any third party, can call `dispatch()` directly at any time.

## Finding Description
`CallDispatcher.dispatch()` is declared `external` with no modifier: [1](#0-0) 

It executes each `Call{to, value, data}` from the caller-supplied array using the `CallDispatcher` contract's own `msg.sender` identity and balance — not the balance of the app that invoked it. It also accepts arbitrary ETH deposits via an open `receive()`: [2](#0-1) 

The dispatcher is intentionally shared across all apps that support "calldata execution": `IntentGatewayV2`/`IntentsBase` uses it for pre-dispatch (swap-then-escrow) and post-dispatch (fill-then-act) calls, transferring input/output tokens to the dispatcher, invoking `dispatch()`, then sweeping the resulting balance back: [3](#0-2) [4](#0-3) 

`HyperFungibleToken`/`WrappedHyperFungibleToken` also route arbitrary cross-chain-message calldata through the same dispatcher after minting/unlocking tokens: [5](#0-4) 

Because the sweep logic in `_execute`/`IntentGatewayV2` only recovers balances for the tokens explicitly declared in `order.output.assets` / `order.inputs`, any token or native ETH left on the dispatcher as a side effect of executing solver/user-supplied `Call[]` data (e.g. an intermediate hop token from a multi-hop DEX swap, leftover WETH, reward tokens accrued from an approve-then-spend call, or excess native value) is **not** guaranteed to be swept in the same transaction. Since the dispatcher is a long-lived, address-stable, shared singleton, that residual balance persists on-chain until something calls `dispatch()` again. Because `dispatch()` has no caller restriction, any unprivileged actor can race to call it directly with a `Call[]` that transfers that residual balance to themselves, stealing value that should have gone back to the protocol (as dust) or to the order's rightful token flow.

The project's own documentation confirms this residual-balance risk is a known operational hazard ("the dispatcher contract holds tokens temporarily during execution"; approvals should be exact, not unlimited), but the control that is missing is not "use exact approvals" — it is that `dispatch()` itself should never be callable by an arbitrary, unauthenticated address in the first place: [6](#0-5) 

## Impact Explanation
Any residual token/ETH balance transiently or accidentally left on the shared `CallDispatcher` — arising from ordinary use of the intent-gateway's pre/post-dispatch calldata feature or the HFT calldata-execution feature — is directly stealable by any address, with no proof, signature, or privileged role required. This is a direct theft-of-funds primitive: the attacker needs only to observe the dispatcher's balance and submit one transaction calling `dispatch()` with a `Call[]` that moves the asset to themselves.

## Likelihood Explanation
The intent-gateway and HFT calldata-execution features are explicitly designed to route third-party-composable calls (swaps, DEX interactions, DeFi deposits) through this dispatcher, and multi-hop/DeFi interactions routinely produce non-zero intermediate-token or ETH residues that the app-level sweep logic (keyed only to the order's declared asset list) does not account for. Any solver, filler, or user constructing an order with `predispatch`/`postdispatch` calldata, or any cross-chain HFT message with calldata, can create such a residue, and any bystander (or the same actor, front-running the next legitimate sweep) can then steal it — this requires no special access and is reachable purely through the intent-solver / token-bridger paths the assessment scope covers.

## Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the specific app/contract instance that funded it for that call (e.g., pass and check an authorized caller, or make the dispatcher per-app/per-call rather than a single shared singleton with an open entry point), and/or ensure the dispatcher sweeps its *entire* balance for every token or asset actually touched by the executed calls (not only the tokens declared in the order), so no persistent, externally drainable balance can accumulate on the shared contract between transactions.

## Proof of Concept
1. A solver fills an `IntentGatewayV2` order whose `output.call` (postdispatch calldata) performs a multi-hop swap through `CallDispatcher`, and the intermediate/reward token received is not listed in `order.output.assets`.
2. `_execute()` sweeps only the assets in `order.output.assets`, leaving the unlisted intermediate token balance sitting on `CallDispatcher`.
3. Any third party observes this residual balance and calls `CallDispatcher.dispatch(abi.encode([Call({to: residualToken, value: 0, data: transfer(attacker, balance)})]))` directly — this succeeds because `dispatch()` has no access control — transferring the residual tokens to the attacker.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

**File:** evm/src/utils/CallDispatcher.sol (L41-62)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L258-299)
```text
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

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
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

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
