### Title
`CallDispatcher.dispatch()` has no caller restriction and lets anyone drain any tokens or ETH sitting in the shared dispatcher contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` executes arbitrary attacker-supplied `Call[]` — including ERC-20 `transfer`/`approve` calls and raw ETH sends — from the `CallDispatcher` contract's own context, with no check on `msg.sender`. This is the same bug class as `RollerPeriphery::approve()`: a public function that lets anyone move assets held by the contract to any destination, because the function itself carries no authorization.

### Finding Description
`CallDispatcher` is a shared utility used by `IntentGatewayV2`/`IntentsBase` (predispatch/postdispatch order execution) and by `HyperFungibleToken`'s calldata-execution feature, where tokens are minted or transferred directly to the `CallDispatcher` address so that subsequent calls can spend them: [1](#0-0) 

```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
```

There is no modifier restricting the caller (no `onlyHost`, `onlyGateway`, or ownership check) — `dispatch()` is `external` and callable by anyone, executing arbitrary `to.call{value}(data)` as `CallDispatcher`. The `receive()` function also unconditionally accepts ETH: [2](#0-1) 

This mirrors the reported `RollerPeriphery::approve()` pattern: a periphery/shared contract exposes a privileged, asset-moving primitive (there, `token.safeApprove(to, amount)`; here, an arbitrary `to.call{value}(data)`) with zero access control, and the contract is expected to (transiently) hold third-party funds.

Documentation confirms the dispatcher is designed to hold funds between steps of a flow, e.g. tokens minted directly to `CALL_DISPATCHER` for later use by its own calls: [3](#0-2) 

and `IntentGatewayV2`/`IntentsBase` transferring order inputs/outputs to the dispatcher before invoking `dispatch()`: [4](#0-3) [5](#0-4) 

### Impact Explanation
Because `dispatch()` is fully permissionless, any balance the `CallDispatcher` holds at any point in time — accidental direct token transfers to it, unswept dust from a partially completed predispatch/postdispatch flow, tokens minted to it as part of a cross-chain calldata-execution message before the follow-up dispatch call executes, or ETH sitting in it via `receive()` — can be stolen outright by any attacker who front-runs or simply calls `dispatch()` with a `Call{to: token, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)}` (or a raw ETH transfer `Call`). This is concrete theft of funds held by an in-scope contract, matching the report's "steal contract tokens" impact class.

### Likelihood Explanation
`CallDispatcher` is a single shared, stateless-looking utility reused across `IntentGatewayV2`, `IntentsBase`, and cross-chain `HyperFungibleToken` calldata execution. Any deviation from perfect intra-transaction atomicity in these flows (a token that receives more than tracked, a failed/partial sweep, funds minted to the dispatcher awaiting a later dispatch call, or plain user error sending tokens to the well-known dispatcher address) leaves it holding assets that are then permanently exposed, since `dispatch()` itself performs no ownership check at all — the likelihood of *some* balance passing through it at *some* point is high given how integrated it is into the intents and HFT calldata-execution paths.

### Recommendation
Restrict `dispatch()` to only be callable by the authorized calling contracts (e.g., the specific `IntentGatewayV2`/`IntentsBase` instance(s) and `HyperFungibleToken` instance(s) that are meant to use it), for example via an `onlyAuthorizedCaller` allowlist set at construction/configuration, or by making `CallDispatcher` a non-shared, per-caller-deployed instance so no third party can invoke `dispatch()` on a dispatcher holding another party's funds.

### Proof of Concept
1. `CallDispatcher` at some point holds an ERC-20 balance or ETH (e.g., dust left over from an `IntentGatewayV2` predispatch/postdispatch flow, or tokens minted to it via `HyperFungibleToken` calldata execution awaiting the follow-up dispatch call).
2. An attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]))` directly — no permission check blocks this.
3. `dispatch()` executes `token.call(...)` as `CallDispatcher`, transferring the balance to the attacker.

Note: I could not fully verify, within the available context, whether `HyperFungibleToken`'s mint-to-`CallDispatcher` and its subsequent `dispatch()` call are guaranteed to execute atomically within the same `onAccept` transaction (which would narrow, but not eliminate, the exploit window to leftover/dust balances). Confirming that ordering in `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`'s `onAccept` would sharpen the exact attack window, but the core issue — `dispatch()` having no access control on a contract designed to (even transiently) hold funds — is independently confirmed from `CallDispatcher.sol` itself.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-63)
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
}
```

**File:** docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx (L149-162)
```text
IHyperFungibleToken(tokenAddress).send{value: nativeFee}(
    IHyperFungibleToken.SendParams({
        dest: StateMachine.evm(42161),
        // mint to the CallDispatcher so the swap can spend the tokens
        to: abi.encodePacked(CALL_DISPATCHER),
        amount: amount,
        timeout: 3600,
        relayerFee: relayerFee,
        data: abi.encode(calls)
    })
);
```

Tokens are minted to `to` first, then the `CallDispatcher` executes each call in sequence. If the calls need to spend the minted tokens, set `to` to the `CallDispatcher` address so tokens are minted directly to the dispatcher.
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-260)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```
