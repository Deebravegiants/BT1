Confirmed: `CallDispatcher.dispatch()` has no caller restriction whatsoever — it's an unauthenticated, permissionless executor of arbitrary `to.call{value}(data)` from its own contract identity, exactly the same root-cause pattern (unrestricted arbitrary target+calldata execution from a shared contract's own context) as the `GeneralRepay.repayJUSD` finding.

### Title
Unrestricted `CallDispatcher.dispatch()` allows theft of any token balance the shared dispatcher temporarily holds - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single shared, permissionless utility contract used by `IntentGatewayV2` (predispatch/postdispatch), `HyperFungibleToken`, and `WrappedHyperFungibleToken` to execute arbitrary attacker-or-user-specified `Call[]` batches from its own address. `dispatch(bytes)` has no access control (no `onlyGateway`/`onlyHost`/allowlist check), so any address can invoke it directly at any time to move whatever token balance or ETH the dispatcher currently holds.

### Finding Description
`CallDispatcher.dispatch` is `external` with zero authentication: [1](#0-0) 
It decodes an attacker-supplied `Call[]` and executes each entry via `to.call{value: call.value}(call.data)`, where `to` is only checked for having code — not for being the token/router the caller intends, nor whether the caller is one of the trusted apps (`IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken`).

Multiple apps route tokens through this dispatcher and rely on it temporarily holding balances between deposit and sweep:
- `IntentGatewayV2.placeOrder` transfers `predispatch.assets` to the dispatcher, calls `dispatch(order.predispatch.call)` to run the user's swap, then makes a *second, separate* `dispatch(...)` call to sweep the resulting balance back to the gateway: [2](#0-1) 
- `IntentsBase._execute` (postdispatch fill flow) mints/sends output tokens to the dispatcher, runs `order.output.call` via `dispatch`, then separately sweeps any residual balances back as "dust": [3](#0-2) 
- `HyperFungibleToken`/`WrappedHyperFungibleToken` mint or unlock tokens directly to the `CallDispatcher` address and forward `Call[]` calldata to it for composable swap/stake workflows: [4](#0-3) 

Because `dispatch()` accepts calls from *any* caller, and because `to.call(data)` executes with `msg.sender == CallDispatcher`, an attacker can submit `Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})` directly to the dispatcher. This does not require any allowance — a plain `transfer()` from the dispatcher's own balance suffices, since the dispatcher is the token holder. Any residual balance left on the shared dispatcher — from an incompletely-swept token not enumerated in `order.output.assets`/`order.inputs` (e.g. a postdispatch swap that routes through an intermediate token the sweep loop never iterates over), from a reverted/partial sweep, or simply a race where any transaction observes non-zero dispatcher balance between the deposit step and the sweep step — is fully exposed to draining by an unrelated third party.

This mirrors the `GeneralRepay.sol` root cause precisely: a contract that executes attacker-influenceable `(target, calldata)` from its own address with no restriction on caller or target, letting anyone repurpose balances/approvals that contract holds for its own benefit.

### Impact Explanation
Any token balance or native ETH the `CallDispatcher` is holding at the moment an attacker's transaction lands — whether transient dust, a token type not covered by an app's own sweep enumeration, or funds left mid-sequence — can be redirected to an attacker with a single unauthenticated call. Because the dispatcher is shared across every app on the deployment (IntentGatewayV2, HyperFungibleToken, WrappedHyperFungibleToken, and any future app that reuses it), this is a protocol-wide, unbounded-value primitive rather than a bug scoped to one app.

### Likelihood Explanation
Exploitation requires no privileged position: the attacker only needs to detect (via mempool/state monitoring) that `CallDispatcher` holds a spendable balance and race a plain transaction calling `dispatch()`. Given the documented sweep logic only iterates tokens explicitly listed in `order.inputs`/`order.output.assets`, any postdispatch/predispatch calldata that produces or leaves value in a token outside that enumerated set (a realistic occurrence for multi-hop swaps, intermediate wrap/unwrap steps, or reverted partial fills) creates a directly exploitable window.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allowlist (e.g., `onlyAuthorizedCaller` mapping maintained by governance, populated with the deployed `IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken` addresses), or make the dispatcher single-use/ephemeral per invocation (e.g., deploy a minimal-proxy dispatcher instance per call, or require the calling app to pass a session token verified against transient storage set atomically by that app). Additionally, ensure every sweep path accounts for **all** tokens the executed calldata could have touched, not just the statically enumerated input/output token list, and consider adding a reentrancy guard to `dispatch()` itself.

### Proof of Concept
1. Monitor for any transaction (e.g., `IntentGatewayV2.placeOrder` with `predispatch.call`, or an HFT calldata-execution mint) that transfers tokens to the well-known `CallDispatcher` address before its own sweep call executes.
2. If the app's postdispatch/predispatch calldata routes through an intermediate token that isn't in the sweep's `order.inputs`/`order.output.assets` list (or any other scenario leaving non-zero balance on the dispatcher after the app's own logic returns), submit:
   `CallDispatcher.dispatch(abi.encode([Call({to: leftoverToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, leftoverToken.balanceOf(dispatcher))})]))`
3. Because `dispatch()` performs no caller check, this call succeeds and transfers the dispatcher's balance to the attacker, regardless of which app or user originally deposited it.

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L86-96)
```text
## Calldata Execution

Both contracts support optional calldata execution on the destination chain via the `CallDispatcher`. By passing a non-empty `data` field in `SendParams`, the sender can trigger arbitrary contract calls on the destination chain immediately after tokens are minted or unlocked. This enables composable cross-chain workflows like transfer-and-swap (e.g., bridge USDC then swap to WETH via UniswapV2), transfer-and-stake, or transfer-and-deposit into a lending protocol — all in a single cross-chain operation.

The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.
```
