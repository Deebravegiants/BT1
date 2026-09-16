### Title
Unrestricted `CallDispatcher.dispatch()` Permits Any Unprivileged Actor to Steal Residual Funds Held by the Shared Executor Contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is `external` with no caller restriction, no reentrancy guard, and no ownership/allow-list check. It is deployed once and shared as `_params.dispatcher` / `_dispatcher` across multiple production apps — `IntentGatewayV2` (predispatch/postdispatch calldata), `HyperFungibleTokenUpgradeable.onAccept`, and `WrappedHyperFungibleTokenUpgradeable.onAccept` — each of which transiently routes user/protocol funds through it and then sweeps back only the tokens it explicitly expects. [1](#0-0) 

### Finding Description
`dispatch()` decodes an arbitrary `Call[]` and executes each entry with `to.call{value: call.value}(call.data)` in the `CallDispatcher`'s own storage/msg.sender context — meaning any `to.call` executes *as* the dispatcher. Nothing gates who may invoke `dispatch()`: [2](#0-1) 

The dispatcher is intentionally shared and reused by unrelated apps and unrelated orders/messages, per the SDK docs and multiple call sites (`_params.dispatcher` in `IntentGatewayV2`/`IntentsBase`, `_dispatcher` in `HyperFungibleTokenUpgradeable`/`WrappedHyperFungibleTokenUpgradeable`): [3](#0-2) [4](#0-3) 

In `IntentGatewayV2.placeOrder`, only the tokens explicitly listed in `order.inputs` are swept back from the dispatcher after the predispatch call executes; the sweep loop is scoped strictly to `inputsLen` (i.e., `order.inputs`), and likewise `_execute` in `IntentsBase.sol` sweeps only `order.output.assets`: [5](#0-4) [6](#0-5) 

Any byproduct token that isn't in the enumerated set (e.g., a swap leg's intermediate/output token, reward tokens, airdrops, or excess produced by a `Call[]` the order/message creator supplies) is left stranded in the dispatcher's balance across transactions. Likewise, the dispatcher's `receive()` accepts native value from anyone with no bookkeeping. Because `dispatch()` has zero access control, any unprivileged third party can later submit their own `Call[]` (e.g., `token.transfer(attacker, balance)` or forwarding stranded ETH) and drain whatever balance the shared dispatcher happens to hold at that moment — funds that in fact belong to the protocol/dust-collection flow or to a residual state left by a completely different user's order/message.

The docs even acknowledge the dispatcher "holds tokens temporarily during execution" and warn against unlimited approvals in `Call[]`, but do not address the unrestricted-caller issue itself: [7](#0-6) 

### Impact Explanation
Concrete permanent theft of funds: any ERC20 or native balance that ends up resident in the singleton `CallDispatcher` (dust from swaps/fee-on-transfer tokens not in the enumerated asset list, byproducts of arbitrary order/message `Call[]` execution, or misdirected native transfers to its payable `receive()`) can be swept out by any unprivileged caller with a single permissionless `dispatch()` call, with no relationship to the original order/message required. Because the same dispatcher instance backs `IntentGatewayV2`, `HyperFungibleTokenUpgradeable`, and `WrappedHyperFungibleTokenUpgradeable`, the blast radius spans the intents and token-bridging surfaces.

### Likelihood Explanation
High — the entrypoint requires no privilege, no proof, and no relayer role; an attacker only needs to observe the dispatcher's on-chain balance (public) and submit a normal transaction with a self-serving `Call[]`. Any order/message whose `Call[]` produces an off-list token or over-collects native value (a routine occurrence with DEX swaps, LP unwraps, and fee-on-transfer tokens described in the gateway's own comments) creates an exploitable window.

### Recommendation
Restrict `CallDispatcher.dispatch()` to be callable only by the authorized app contracts that own the current flow (e.g., an `onlyAuthorized`/allow-list of registered apps, or make the dispatcher single-use/ephemeral per call via `CREATE2`/minimal-proxy per invocation), and/or add a generic sweep-all/rescue mechanism gated to the intended app so any residual balance is reclaimed by the protocol rather than left permissionlessly drainable. At minimum, enforce zero-balance invariants (revert if `to` token balance is nonzero after intended sweeps) so dust cannot silently accumulate in a publicly callable contract.

### Proof of Concept
1. Any user calls `IntentGatewayV2.placeOrder` with a `predispatch.call` that swaps token A for token B via an external router, where `order.inputs` only lists token A/token B amounts required but the swap also yields a small amount of token C (e.g., router reward token, or rounding remainder of an intermediate hop) — this token C balance remains on the shared `CallDispatcher` after the transaction, since the sweep loop only iterates `order.inputs`.
2. An unrelated attacker later calls `CallDispatcher.dispatch(abi.encode([Call({to: tokenC, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, tokenC.balanceOf(dispatcher))})]))` directly — this succeeds because `dispatch()` has no caller restriction, and `tokenC.transfer` executes with `msg.sender == CallDispatcher`, sending the stranded balance to the attacker.
3. The same technique applies to native value stranded via the dispatcher's unrestricted `receive()`, or to residual balances left by `HyperFungibleTokenUpgradeable`/`WrappedHyperFungibleTokenUpgradeable`'s `onAccept` calldata execution path (`ICallDispatcher(_dispatcher).dispatch(message.data)` at [8](#0-7) ), which performs no post-execution sweep at all.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L260-289)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-534)
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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
