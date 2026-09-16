### Title
Unauthenticated `CallDispatcher.dispatch()` lets any address drain funds stranded in the shared dispatcher contract - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher.dispatch()` is a public, unauthenticated entrypoint that executes an arbitrary attacker-supplied `Call[]` "in its own context" with whatever native ETH or token balance the contract currently holds [1](#0-0) . This mirrors the CVE-2019-1003006 bug class — an endpoint that accepts and executes an unprivileged, attacker-controlled "script" (here, an ABI-encoded call sequence) with no permission check on the caller.

### Finding Description
`CallDispatcher` is deployed once and shared across multiple applications (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`, and their variants) as documented in the token/intent overview pages [2](#0-1) . Its `dispatch` function has no `onlyApp`/`msg.sender` restriction whatsoever:

```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
``` [3](#0-2) 

The contract also has a permissionless `receive()` that accepts native ETH from anyone [4](#0-3) . Multiple call sites route escrowed user/solver funds through this contract mid-transaction, and the protocol's own documentation explicitly warns that token approvals set inside the `Call[]` should use exact amounts "since the dispatcher contract holds tokens temporarily during execution" [5](#0-4) , and that any token balance not accounted for by an order's declared `output.assets` is only swept for the tokens the caller explicitly lists [6](#0-5) . Anything else that ends up on the dispatcher (fee-on-transfer remainders, unexpected reward/airdrop tokens acquired by a swap inside `predispatch`/`postdispatch` calls, unswept ETH dust, or ETH sent directly via `receive()`) is not tracked by any owner of the contract — it is simply an unclaimed balance sitting on an address whose `dispatch()` function anyone can call to move that balance anywhere.

Because `dispatch()` performs no `msg.sender` check and the `to` target only needs to have code (`extcodesize(to) > 0`), any unprivileged EOA can submit a single transaction directly to `CallDispatcher.dispatch()` with a `Call[]` such as `{to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, allBalance)}` or `{to: attacker, value: address(this).balance, data: ""}`, taking whatever is currently stranded there.

### Impact Explanation
This is theft of protocol/user funds: any stranded ETH or ERC20 balance on the shared `CallDispatcher` — dust from imperfect sweeps in `IntentsBase._execute`/`IntentGatewayV2` predispatch flows, fee-on-transfer remainders, or accidental ETH transfers — can be permissionlessly swept by an unrelated attacker rather than the intended beneficiary (protocol treasury via governance sweep, or the escrow accounting in `IntentsBase`). Since the dispatcher is shared across `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` deployments, the blast radius spans multiple apps on the same chain.

### Likelihood Explanation
High likelihood: reachable from a single, unprivileged transaction with no proof, consensus verification, or governance action required. Any dust generation event (fee-on-transfer tokens, partial fill rounding, a swap returning an unlisted reward token, or a stray ETH transfer to the dispatcher) creates an immediately, permissionlessly sweepable balance; MEV searchers/bots can trivially monitor the dispatcher's balances and front-run legitimate sweep attempts.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allowlist (e.g., an `onlyAuthorizedCaller` modifier enforcing `msg.sender` is one of the registered app contracts), or make each app deploy/own its own dispatcher instance so stranded balances cannot be swept by unrelated third parties. Additionally, ensure every code path that transiently parks funds on the dispatcher performs an exhaustive sweep (including any tokens/ETH not explicitly declared in `order.output.assets`) before returning control, and reject sending `receive()` funds without a corresponding accounted-for operation.

### Proof of Concept
1. A `fillOrder`/`send` flow using `IntentGatewayV2`/`HyperFungibleToken` executes a `postdispatch` `Call[]` through `ICallDispatcher(dispatcher).dispatch(...)` that swaps output tokens via a DEX; the swap returns a small amount of an unlisted reward token or leaves ETH dust that the sweep loop in `IntentsBase._execute` does not account for (only `order.output.assets` are swept) [6](#0-5) .
2. An attacker observes the dispatcher's non-zero token/ETH balance on-chain.
3. The attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]))` directly — no authorization check prevents this [3](#0-2)  — and receives the stranded funds.

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
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
