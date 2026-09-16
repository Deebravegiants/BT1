## Title
Unrestricted `CallDispatcher.dispatch()` allows any unprivileged caller to drain stranded tokens/ETH left behind after order/token calldata execution - (File: `evm/src/utils/CallDispatcher.sol`)

## Summary
The Li.finance incident stemmed from a shared contract that executed arbitrary calldata and could be leveraged to move funds/approvals it held without any authorization check tying the caller to the funds being moved. Hyperbridge's `CallDispatcher` — the shared executor used by both `IntentGatewayV2` (predispatch/postdispatch) and `HyperFungibleToken`/`WrappedHyperFungibleToken` (calldata-on-receive) — has the exact same structural weakness: its `dispatch()` entrypoint is completely public with no caller restriction, and the contract is designed to transiently hold user/solver funds and grant token approvals to routers while executing arbitrary `Call[]` batches.

## Finding Description
`CallDispatcher.dispatch()` takes an ABI-encoded `Call[]` and executes each call sequentially with no access control at all: [1](#0-0) 

There is no `onlyGateway`/`onlyHost` style modifier, no check on `msg.sender`, and the contract also has a permissionless `receive()` function that accepts ETH from anyone: [2](#0-1) 

This contract is a single shared singleton referenced by `_params.dispatcher` and used by multiple apps to route escrowed/bridged funds through arbitrary DeFi calls (e.g., Uniswap swaps) before sweeping the result back to the caller:

- `IntentGatewayV2.placeOrder` transfers `order.predispatch.assets` to the dispatcher, invokes `dispatch(order.predispatch.call)`, then sweeps back **only the tokens listed in `order.inputs`**: [3](#0-2) 

- `IntentsBase._execute` executes `order.output.call` via the dispatcher and sweeps back **only the tokens listed in `order.output.assets`**: [4](#0-3) 

- `HyperFungibleToken.onAccept`/`WrappedHyperFungibleTokenUpgradeable.onAccept` mint/unlock tokens to `to` (which the docs explicitly recommend setting to the `CallDispatcher` address) and then forward user-supplied `message.data` straight into `dispatch()`: [5](#0-4) 

Because the dispatcher only sweeps back the specific token set the calling app anticipated (input tokens, output tokens), any token produced as a side effect of the arbitrary calldata execution that is *not* in that enumerated set — e.g. an intermediate hop token from a multi-hop swap, a reward/referral token, dust from rounding, or leftover native ETH sent via `receive()` — is left stranded in the `CallDispatcher`. Because `dispatch()` has no access control, **any unprivileged address** can subsequently call `CallDispatcher.dispatch()` directly with a `Call[]` that transfers this stranded balance to itself, or that leverages any standing ERC20 approvals the dispatcher previously granted to a swap router (via a documented "approve then swap" pattern, e.g. `IERC20.approve(UNISWAP_V2_ROUTER, amount)`) to route out tokens the dispatcher is currently holding — including a legitimate order's or transfer's funds if they land in the dispatcher just before or during separate transactions that don't fully sweep them.

## Impact Explanation
Because `dispatch()` is reachable by anyone and is shared across every `IntentGatewayV2` order and every `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata-bearing transfer, any funds or standing router approvals accidentally or transiently left in the `CallDispatcher` are permanently exposed to theft by an unprivileged third party. This is a direct funds-theft path analogous to the Li.finance root cause: an arbitrary-call executor whose custody of tokens/approvals is not gated to the party that deposited them.

## Likelihood Explanation
Triggering the underlying condition only requires crafting an order/transfer whose `predispatch`/`postdispatch`/`data` calldata produces a token or ETH residue outside the enumerated sweep set (e.g., a multi-hop swap path, a reward token from a DEX, or leftover ETH), which is entirely controllable by the order placer/solver themselves (self-inflicted or attacker-crafted order). Once any balance is stranded, exploitation is a single unauthenticated call to `CallDispatcher.dispatch()` — no proofs, no consensus verification, no privileged role required.

## Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the registered gateway/token contracts that own the current execution context (e.g., an `onlyAuthorizedCaller` allowlist configured at deployment), and/or make the dispatcher non-custodial across calls by requiring the caller to atomically specify and sweep back *all* resulting token balances (not just the pre-declared input/output set) within the same transaction, reverting if any residual balance remains. Revoke router approvals (`forceApprove(router, 0)`) after each call batch rather than leaving standing max approvals.

## Proof of Concept
1. A user places an `IntentGatewayV2` order with `predispatch.call` that performs a multi-hop swap through the `CallDispatcher` producing an intermediate token not listed in `order.inputs` (e.g., swap ETH → TOKEN_A → TOKEN_B, but only TOKEN_B is declared as the order input).
2. `placeOrder` sweeps back only the declared `order.inputs` tokens; the intermediate `TOKEN_A` residue (or ETH dust) remains in the shared `CallDispatcher`.
3. Any external address then calls `CallDispatcher.dispatch(abi.encode([Call({to: TOKEN_A, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, strandedBalance)})]))` directly — this succeeds because `dispatch()` performs no caller authorization check — draining the stranded balance to the attacker. [6](#0-5)

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

**File:** evm/src/apps/IntentGatewayV2.sol (L234-270)
```text
        uint256 msgValue = msg.value;
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-540)
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
