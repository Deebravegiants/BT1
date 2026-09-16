## Title
CallDispatcher.dispatch() has no access control, letting anyone drain any token/ETH balance stuck in the shared dispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch()` is `external` with no caller restriction — any address can invoke it to make the dispatcher execute arbitrary `Call[]` with arbitrary `value`/`calldata`, exactly analogous to `PeripheryPayments.sweepToken()` being callable by anyone. Since `CallDispatcher` is a single shared contract used by `IntentGatewayV2`/`IntentsBase` and the `HyperFungibleToken`/`WrappedHyperFungibleToken` flows to hold assets *transiently* mid-transaction, any token or native balance left on it — intentionally or by accident — can be swept out by an unrelated third party. [1](#0-0) 

### Finding Description
`dispatch()` has zero access control — it is a bare `external` function that decodes an attacker-supplied `Call[]` and executes each entry against `to.call{value: call.value}(call.data)`:

```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
``` [2](#0-1) 

Multiple in-scope apps route funds through this exact contract and rely on it holding tokens/ETH only momentarily within a single atomic transaction:

- `IntentGatewayV2.placeOrder` transfers predispatch assets to the dispatcher, invokes `dispatch()`, and then issues a second `dispatch()` call that sweeps the *entire* balance of each `order.inputs[]` token back to the gateway. [3](#0-2) 

- `IntentsBase._execute` runs a filler's arbitrary output calldata via the dispatcher, then sweeps back only the tokens enumerated in `order.output.assets`: [4](#0-3) 

- The `HyperFungibleToken`/`WrappedHyperFungibleToken` flow mints/unlocks tokens to the `CallDispatcher` and forwards arbitrary calldata (e.g., approve+swap) for it to execute, explicitly noting "the dispatcher contract holds tokens temporarily during execution." [5](#0-4) 

Because `dispatch()` is permissionless, any residual balance the dispatcher accumulates — for example, an intermediate token produced by a filler's postdispatch swap that isn't included in `order.output.assets`, dust from a partially-executed multi-hop swap, or tokens sent to the dispatcher by mistake — is not protected by any owner/gateway-only check and can be pulled out by literally anyone constructing their own `Call[]` and calling `dispatch()` directly, bypassing `IntentGatewayV2`/`IntentsBase` entirely. This is the same root cause as the reported `PeripheryPayments.sweepToken()` bug: a balance-draining entry point with no `msg.sender` restriction on a contract that is expected to (even transiently) hold protocol/user funds.

### Impact Explanation
Any token or native-asset balance that ends up sitting on the shared `CallDispatcher` — due to unswept postdispatch residue, leftover dust from multi-hop DEX routes, or tokens sent there by mistake — is immediately and permanently stealable by any unprivileged actor who calls `dispatch()` directly. Since the dispatcher is shared across `IntentGatewayV2` order fills and `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution, the blast radius spans multiple products' escrowed/solver funds. This is a direct theft primitive, qualifying as High severity per the analog report.

### Likelihood Explanation
The likelihood hinges on the dispatcher actually holding a non-zero balance at some point outside the atomic sweep performed by the calling app. This is plausible in practice: `_execute`'s sweep is scoped only to `order.output.assets`, so any solver-supplied calldata that produces a *different* token than what's declared in the order's outputs leaves that token permanently stuck and drainable. No proof or governance action is required to exploit — a bare call to `dispatch()` with a `Call` targeting the leftover token's `transfer` function is sufficient.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by an allow-listed set of caller contracts (e.g., a mapping of authorized gateways/apps set at deploy time or via governance), or convert the dispatcher into a pattern where it never holds residual balance beyond a single call (e.g., always sweep the caller-specified list plus a native/ERC20 catch-all in the same transaction, and revert if extraneous balances remain). At minimum, add an owner/governance-gated rescue mechanism and remove open executability of `dispatch()` from arbitrary EOAs/contracts.

### Proof of Concept
1. A solver fills an `IntentGatewayV2` order whose `output.call` performs a multi-hop swap producing token `X` as an intermediate along with the declared output token `Y`.
2. `_execute` sweeps only `Y` (per `order.output.assets`), leaving residual `X` balance on the shared `CallDispatcher`. [6](#0-5) 
3. An unrelated attacker calls `CallDispatcher.dispatch()` directly with a `Call[]` of `{to: X, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)}`. [2](#0-1) 
4. Since `dispatch()` has no caller restriction, the transfer succeeds and the attacker walks away with the stranded token `X`, with no relation to the original order.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L258-289)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-544)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-97)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

```
