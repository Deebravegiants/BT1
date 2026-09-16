### Title
`CallDispatcher.dispatch()` has no access control, letting any unprivileged caller drain funds parked on the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch(bytes memory encoded)` executes an arbitrary ABI-decoded `Call[]` array — each entry an arbitrary `(to, value, data)` triplet — with no caller restriction whatsoever [1](#0-0) . This mirrors the guake CVE-2021-23556 pattern exactly: a powerful "execute arbitrary command" primitive is exposed with no check on who is invoking it, relying entirely on the assumption that only the trusted caller (the intent gateway / token contract) will ever call it and that the dispatcher never holds a balance when an untrusted party could reach it.

### Finding Description
`CallDispatcher` is a single shared, stateful contract (`_params.dispatcher`) reused across every `placeOrder`/`fillOrder` call in `IntentGatewayV2` (both the mainline and Tron variants) for predispatch/postdispatch calldata execution [2](#0-1) [3](#0-2) , and it is also invoked from `HyperFungibleTokenUpgradeable.onAccept` to run cross-chain `data` payloads after tokens are minted [4](#0-3) .

Every one of these call sites assumes the dispatcher will end each transaction empty: after predispatch/postdispatch calls run, the gateway sweeps back only the tokens it explicitly knows about (`order.inputs`/`order.output.assets`) [5](#0-4) . Any token or native ETH that ends up on the dispatcher outside that enumerated set — e.g. a DEX swap in the calldata that yields extra/unlisted tokens, partial slippage refunds, or a stray native transfer — is left sitting on the contract. Because `dispatch()` has no `onlyOwner`/`onlyGateway`/`onlyHost` guard, any address — an unprivileged relayer, solver, or MEV bot — can call `CallDispatcher.dispatch()` directly with a `Call[]` targeting that leftover balance (`to: token, data: transfer(attacker, balance)`, or `to: attacker, value: balance`) and pull it out for themselves.

This is structurally identical to the guake advisory: a method capable of executing arbitrary attacker-supplied instructions against a resource the contract is trusted to hold is reachable by any unprivileged caller with no authentication of who is allowed to invoke it.

### Impact Explanation
Any token/ETH balance that is not perfectly swept off `CallDispatcher` between order fills or postdispatch executions is permanently exposed to theft by any address, front-runnable at will since `dispatch()` is a plain external call with no reentrancy/ownership guard. Given the dispatcher is a shared singleton across all orders and both `IntentGatewayV2` and `HyperFungibleToken` calldata paths, this creates a persistent, protocol-wide siphon for any dust or unswept asset — concrete theft of funds that were meant to be swept back to the gateway/treasury as protocol dust.

### Likelihood Explanation
Likelihood is elevated because:
- Predispatch/postdispatch calldata is attacker-influenced input (arbitrary DEX routes, swaps with slippage, multi-hop paths) that commonly yields balances the gateway's sweep logic does not anticipate (only `order.inputs`/`order.output.assets` are swept).
- `dispatch()` is a public, permissionless entry point on a well-known, address-discoverable contract, so any bot watching the dispatcher's token balances can react instantly.
- No privileged action (governance, admin, malicious node) is required — a single unprivileged actor calling `dispatch()` is sufficient.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allowlist (e.g. `onlyOwner`/`onlyGateway`, or a constructor-bound authorized caller set at deployment), and/or make the dispatcher non-custodial across transactions by requiring it to revert if it retains any balance of tokens not explicitly swept at the end of each `dispatch()` invocation.

### Proof of Concept
1. A solver fills an order whose `order.output.call` performs a multi-hop swap that yields a small amount of an intermediate token not present in `order.output.assets`.
2. `IntentsBase._execute` sweeps only the tokens named in `order.output.assets`; the intermediate token balance remains on `CallDispatcher` [5](#0-4) .
3. Any third party calls `CallDispatcher.dispatch(abi.encode([Call({to: intermediateToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, leftoverBalance)})]))` directly — this succeeds because `dispatch()` performs no caller check [1](#0-0) , transferring the leftover tokens to the attacker.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-502)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L504-533)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L391-414)
```text

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
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
