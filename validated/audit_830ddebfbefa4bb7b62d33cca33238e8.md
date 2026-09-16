Confirmed: `CallDispatcher` is a single, CREATE2-deployed shared singleton (same address `0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd` on every mainnet chain) used by every Hyperbridge app — `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` — as their common `dispatcher`. Its `dispatch()` function has no access control at all, and its docs explicitly acknowledge "the dispatcher contract holds tokens temporarily during execution," warning callers to use exact-amount approvals rather than unlimited ones — i.e., the design already assumes transient holdings that must not be exploitable. This maps directly onto the DEXRouter bug class: an unauthenticated function that lets anyone drive arbitrary `to.call{value}(data)` from a contract that (even transiently) holds other users' funds.

### Title
Unauthenticated `CallDispatcher.dispatch()` on a shared singleton lets any caller steal approvals/balances left by other users' cross-chain calldata execution - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher.dispatch()` has zero access control and is shared as a single CREATE2 singleton address across every Hyperbridge EVM app (`IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken`) on every chain. Any account whose bridged message or order carries a non-empty `data`/`call` payload can have the dispatcher execute an `approve(attacker, type(uint256).max)` on any ERC20 as part of its "Calldata Execution" feature. Because the dispatcher is a permanent, shared contract instance (not deployed per-message or per-order), this approval persists on-chain indefinitely and is not scoped to the message that created it.

### Finding Description
`CallDispatcher.dispatch()` is `external` with no modifier, and simply decodes a `Call[]` and executes each entry: [1](#0-0) 

Any of the Hyperbridge apps that expose "calldata execution" forward attacker-supplied `Call[]` bytes straight to this dispatcher after moving funds to it, e.g.:
- `WrappedHyperFungibleToken.onAccept`: unlocks/mints tokens to the beneficiary, then unconditionally forwards `message.data` (attacker/sender-controlled) to the shared dispatcher: [2](#0-1) 
- `IntentsBase._execute` (intents v2 postdispatch) dispatches `order.output.call` — attacker/order-author-controlled bytes — through the same shared dispatcher: [3](#0-2) 
- `IntentGatewayV2.placeOrder` predispatch flow sends assets to `_params.dispatcher` and then executes `order.predispatch.call` (fully attacker-controlled): [4](#0-3) 

Because `dispatch()` performs a raw `to.call{value: call.value}(call.data)` with `msg.sender == CallDispatcher`, an attacker can encode a `Call` whose target is any ERC20 token and whose data is `approve(attackerAddress, type(uint256).max)`. This executes with the dispatcher as `msg.sender`, so `allowance[CallDispatcher][attacker]` is permanently set. The docs implicitly acknowledge the dispatcher's transient-holding risk, warning integrators to use exact-amount approvals in `Call[]` "since the dispatcher contract holds tokens temporarily during execution": [5](#0-4) 

The mainnet deployment confirms the dispatcher is one fixed CREATE2 address reused by every app across every chain, not a fresh/isolated instance per operation: [6](#0-5) 

Since the approval is not cleared or scoped to a single message, the very next time *any* user's bridged tokens or predispatch/postdispatch swap output of the *same token type* transiently lands in the dispatcher (which every app in the ecosystem does by design, per the "Calldata Execution" flows above), the pre-planted attacker allowance lets the attacker call `token.transferFrom(CallDispatcher, attacker, amount)` directly — bypassing the legitimate sweep-back logic entirely — and drain that balance before the legitimate app can reclaim it.

### Impact Explanation
This is concrete theft of funds: any user who bridges tokens with calldata execution to the CallDispatcher, or any solver/order whose predispatch/postdispatch swap path routes an intermediate token through it, is exposed to having those transient balances stolen by an attacker who front-loaded a poisoned `approve()` via the dispatcher's unauthenticated `dispatch()` entrypoint on an earlier, unrelated transaction. Because the dispatcher address is identical across `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` deployments on every chain, the blast radius spans the entire fleet of apps sharing that dispatcher instance, not just one integration.

### Likelihood Explanation
High. `dispatch()` requires no privilege whatsoever to call, and any user of the "Calldata Execution" feature (a first-class, documented capability of `HyperFungibleToken`/`WrappedHyperFungibleToken`/`IntentGatewayV2`) can trivially embed a malicious `approve` call in their own legitimate-looking bridge/order payload. The attacker does not need to compromise any component — merely submit one ordinary cross-chain transfer or order with crafted calldata, then wait for/front-run any subsequent transient balance of that token.

### Recommendation
- Add access control to `CallDispatcher.dispatch()` (e.g., an allowlist of authorized callers set at construction, or make the dispatcher deployable per-caller/per-app rather than a shared singleton).
- Ensure the dispatcher never retains ERC20 `approve` state across calls — e.g., have `dispatch()` explicitly revoke any approvals it granted at the end of execution, or disallow `approve`-selector calls to arbitrary spenders inside `Call[]` unless immediately consumed within the same batch.
- Consider deploying a fresh, single-use dispatcher instance (e.g., via minimal proxy/CREATE2 keyed to the message/order commitment) per cross-chain calldata execution rather than reusing one global address, eliminating cross-message state persistence entirely.

### Proof of Concept
1. Attacker calls `HyperFungibleToken.send(...)` (or crafts any order with `predispatch`/`output.call`) with `data` encoding `Call[]{ {to: TOKEN, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)} }`, targeting the shared `CallDispatcher` address.
2. This executes via `ICallDispatcher(dispatcher).dispatch(message.data)` in `onAccept`, so `TOKEN.allowance(CallDispatcher, attacker) = type(uint256).max` is now set permanently: [7](#0-6) 
3. At any later point, when a legitimate user's bridge transfer, or a solver's predispatch/postdispatch swap involving `TOKEN`, causes `TOKEN` balance to transiently land on the same `CallDispatcher` (per the documented "set `to` to the `CallDispatcher` address so tokens are delivered directly to it" pattern): [8](#0-7) 
4. Attacker calls `TOKEN.transferFrom(CallDispatcher, attacker, TOKEN.balanceOf(CallDispatcher))` directly (no interaction with any Hyperbridge contract required), draining the victim's transiting funds before the legitimate app's sweep-back `Call[]` executes.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L322-328)
```text
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L388-414)
```text
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L88-90)
```text
Both contracts support optional calldata execution on the destination chain via the `CallDispatcher`. By passing a non-empty `data` field in `SendParams`, the sender can trigger arbitrary contract calls on the destination chain immediately after tokens are minted or unlocked. This enables composable cross-chain workflows like transfer-and-swap (e.g., bridge USDC then swap to WETH via UniswapV2), transfer-and-stake, or transfer-and-deposit into a lending protocol — all in a single cross-chain operation.

The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```

**File:** docs/content/developers/evm/contract-addresses/mainnet.mdx (L19-27)
```text
| `UniswapV2 (UniV3 Wrapper)` | [`0x98B0eDd13ff99c40A453b88d308C4B21a3Ad0EAc`](https://etherscan.io/address/0x98B0eDd13ff99c40A453b88d308C4B21a3Ad0EAc) |
| `TokenGateway (Deprecated)` | [`0xFd413e3AFe560182C4471F4d143A96d3e259B6dE`](https://etherscan.io/address/0xFd413e3AFe560182C4471F4d143A96d3e259B6dE) |
| `CallDispatcher` | [`0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd`](https://etherscan.io/address/0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd) |
| `IntentGatewayV2` | [`0xAe041F7B0CB581876832830baeB6a2Aa2a3C9716`](https://etherscan.io/address/0xAe041F7B0CB581876832830baeB6a2Aa2a3C9716) |
| `IntentGatewayV2 (Implementation)` | [`0x9d82B05156d0da273D66C5cCbDccef2b00EE06A7`](https://etherscan.io/address/0x9d82B05156d0da273D66C5cCbDccef2b00EE06A7) |
| `SolverAccount` | [`0x7cb55539d1144F62422099c3FA3405092022c88C`](https://etherscan.io/address/0x7cb55539d1144F62422099c3FA3405092022c88C) |
| `SimplexPaymaster` | [`0xD4340d7466e040626383cb9cda9307ba8E081149`](https://etherscan.io/address/0xD4340d7466e040626383cb9cda9307ba8E081149) |
| `SimplexPaymaster (Implementation)` | [`0x58F678b5dA7997C7121621495ECFD8984D525e79`](https://etherscan.io/address/0x58F678b5dA7997C7121621495ECFD8984D525e79) |
| `BandwidthManager` | [`0x6A67533Ce73756FfaB17c05578A5FBBa5d9B2d8d`](https://etherscan.io/address/0x6A67533Ce73756FfaB17c05578A5FBBa5d9B2d8d) |
```
