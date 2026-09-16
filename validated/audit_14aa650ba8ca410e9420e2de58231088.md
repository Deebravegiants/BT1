### Title
Unrestricted `CallDispatcher.dispatch()` allows anyone to drain any token/ETH balance the shared dispatcher happens to hold - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher.dispatch()` is a fully public, unauthenticated `external` function that executes an attacker-supplied `Call[]` array from the dispatcher's own context, with no caller restriction whatsoever [1](#0-0) . The same `CallDispatcher` instance is shared across `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` flows, all of which route tokens or native value through it as an intermediate holder during predispatch/postdispatch calldata execution [2](#0-1) . Whenever any residual token balance or native ETH is left on the dispatcher after a legitimate flow completes — dust from an untracked intermediate swap token, a partially-swept balance, or any other edge case not covered by the caller's own sweep logic — any unrelated third party can call `dispatch()` directly and move those assets out, since the function performs no source/authorization check at all.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` decodes an arbitrary `Call[]` and executes each entry via `to.call{value: call.value}(call.data)` from the dispatcher's own `msg.sender` context [3](#0-2) . There is no `onlyGateway`, `onlyHost`, or any other access-control modifier on this function — it is identical to how a shared "migrator"-style utility contract is normally only meant to be invoked by a trusted orchestrator, but here it is reachable by any EOA or contract in a single transaction.

The dispatcher is designed to hold tokens/ETH only "temporarily" during execution of `IntentGatewayV2` predispatch/postdispatch calls and `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution [4](#0-3) . The `IntentGatewayV2`/`IntentsBase` sweep logic only forwards back the specific `order.inputs`/`order.output.assets` tokens it is aware of [5](#0-4) ; any other token produced as a side effect of arbitrary predispatch/postdispatch calldata (e.g. an intermediate swap hop, a reward token, or a token not declared in the order) is never accounted for and remains stranded on the dispatcher. Likewise, native ETH that lands on the dispatcher via its unconditional `receive()` [6](#0-5)  is only recovered if the caller explicitly includes a sweep call for it.

Because `dispatch()` has no caller restriction, once any balance is stranded on the shared dispatcher — even a small amount of dust from a benign, unrelated user's order — any third party can call `CallDispatcher.dispatch()` directly with a `Call{to: token, value: 0, data: transfer(attacker, balance)}` (for ERC20) or `Call{to: attackerControlledContract, value: balance, data: ""}` (for native ETH, routed through any contract with a receiving fallback, since `dispatch()` only requires the target to have code) to steal it. This is functionally analogous to the Biswap Migrator incident, where a shared helper contract intended to be invoked only as part of a controlled migration flow lacked sufficient access restriction, letting an attacker directly invoke it to move assets it held.

### Impact Explanation
Any ERC20 or native balance stranded on the shared `CallDispatcher` — across any app that uses it (`IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken`) — is permanently and immediately stealable by any unprivileged address, front-runnable the moment it becomes visible on-chain. Since the dispatcher is a single shared, cross-app singleton, dust or stranded funds from one integration's edge case (e.g., an intermediate DEX-hop token from a predispatch swap, or ETH that a caller forgot to sweep) become a race for any observer, resulting in theft of user/protocol funds. This is a concrete theft-of-funds vector reachable from a single submitted transaction and requires no privileged role.

### Likelihood Explanation
Triggering requires (1) some flow leaving a non-zero balance on the dispatcher (plausible given predispatch/postdispatch calldata can route through arbitrary DeFi calls not fully accounted for by the caller's sweep list) and (2) an attacker monitoring the dispatcher's balance and calling `dispatch()` before the legitimate owner sweeps it. Given the dispatcher is a well-known, fixed, and shared address used by every integration, and mempool/state monitoring for stray balances on a well-known contract is trivial and highly incentivized (MEV-style), the likelihood of exploitation once any dust appears is high.

### Recommendation
Add an access-control gate to `CallDispatcher.dispatch()` (e.g., restrict callers to a registered allowlist of gateway/app addresses, or require that the caller pre-fund/repay exactly what it consumes in the same call), or redesign so the dispatcher never custodies un-swept balances across transaction boundaries (e.g., ephemeral per-call proxy contracts via `CREATE2`/`CREATE` instead of a shared singleton). At minimum, ensure every calldata-execution flow (`IntentGatewayV2` predispatch/postdispatch and `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata) exhaustively sweeps *all* token balances (not just the tokens explicitly declared in the order/message) and ETH off the dispatcher before returning control, and add a permissionless "rescue self" sweep restricted to returning funds to the calling app rather than allowing arbitrary target/calldata execution by any caller.

### Proof of Concept
1. A benign `IntentGatewayV2.placeOrder` (or `fillOrder`) with `predispatch.call`/`output.call` performs a multi-hop swap through the `CallDispatcher` that yields a small amount of an intermediate token not declared in `order.inputs`/`order.output.assets` (or leaves dust ETH via `receive()`), which is never swept because `IntentsBase._execute`/`placeOrder` only sweeps the declared input/output tokens [5](#0-4) .
2. This leftover balance now sits on the shared `CallDispatcher` contract.
3. An attacker observes the non-zero balance (e.g. via `IERC20(token).balanceOf(dispatcher)`).
4. The attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]))` directly — no `onlyHost`/`onlyGateway` check exists to stop this [3](#0-2) .
5. The dispatcher executes the transfer from its own balance to the attacker, completing the theft.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

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

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L85-112)
```text
## Calldata

Orders support arbitrary calldata execution at two points in the lifecycle — before escrow (predispatch) and after fill (postdispatch). Both are executed through the `CallDispatcher` contract, which takes an ABI-encoded `Call[]` array:

```solidity
struct Call {
    address to;      // Target contract (must have code, reverts with NotContract otherwise)
    uint256 value;   // ETH to send with call
    bytes data;      // Calldata to execute
}
```

The `CallDispatcher` executes each call sequentially and reverts the entire batch if any call fails.

### Predispatch

The `predispatch` field in `Order` contains calldata to execute *before* escrowing inputs. The predispatch assets specified in `DispatchInfo.assets` are transferred to the `CallDispatcher`, the encoded calls are executed, and the resulting tokens are transferred back to the gateway for escrow. This enables swap-then-escrow patterns — for example, a user sends ETH which the `CallDispatcher` swaps to DAI on Uniswap, and the resulting DAI is escrowed as the order input.

### Postdispatch

The `call` field in `PaymentInfo` contains calldata to execute *after* the order is filled. This enables fill-then-act patterns — for example, output tokens received from the solver are routed through a DeFi protocol before reaching the beneficiary.

Execution timing differs by mode:

- **Same-chain**: Calldata executes only after the order is **fully filled**. Partial fills do not trigger calldata — only the final fill that completes the order executes it. This ensures all output tokens are available when the calls run.
- **Cross-chain**: Calldata executes **immediately** after the solver delivers output tokens to the beneficiary, before the settlement message is dispatched back to the source chain.

After execution, any tokens remaining in the `CallDispatcher` are swept back to the gateway and collected as dust (emitting `DustCollected` for each token). When postdispatch calldata is present, 100% of any surplus (solver overpayment) goes to the protocol rather than being split with the beneficiary — this prevents manipulation of surplus distribution through calldata side effects.
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
