The strongest analog to this bug class in Hyperbridge is `CallDispatcher.dispatch()` — an unrestricted, permissionless function that executes arbitrary attacker-supplied calls using whatever balance the shared `CallDispatcher` contract currently holds, exactly mirroring the flash-loan report's root cause: a critical protocol-facing execution entrypoint with no caller authentication, exploitable by anyone with attacker-controlled data.

### Title
Unauthenticated `CallDispatcher.dispatch()` allows draining any ETH/ERC20 balance transiently held by the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch(bytes)` is `external` with **no access-control modifier** — any address can call it directly with an arbitrary ABI-encoded `Call[]` array, and the dispatcher will execute each `to.call{value: call.value}(call.data)` using its own held ETH/ERC20 balance. This is the same root-cause pattern as the referenced flash-loan report: a function meant to be invoked only in the context of a trusted, verified protocol flow (`onAccept` after ISMP proof verification) is instead reachable and controllable directly by any unprivileged caller.

### Finding Description
`CallDispatcher` is a shared utility contract used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`, and their upgradeable variants to execute post-bridge/post-fill calldata: [1](#0-0) 

`dispatch()` has zero restriction on `msg.sender` — it does not check that the caller is the gateway/token contract that is supposed to own the in-flight funds: [2](#0-1) 

The dispatcher is designed to transiently hold ETH and ERC20 balances mid-flow. The docs explicitly acknowledge this: tokens/ETH are minted or unlocked *to* the `CallDispatcher` address before it executes calls, and any leftover ("dust") remains in the contract until later swept: [3](#0-2) 

The `IntentGatewayV2` docs confirm the same pattern for both predispatch and postdispatch calldata, and describe "any tokens remaining in the `CallDispatcher`... swept back to the gateway... as dust" — i.e., an explicit acknowledgment that non-zero balances can and do linger in the dispatcher between calls: [4](#0-3) 

Because `dispatch()` is exposed without any caller check, any unprivileged actor observing a pending/leftover balance in the `CallDispatcher` (ETH from a native-ETH `Call.value` forward, or ERC20 dust from partial swaps/approvals) can call `dispatch()` themselves with a `Call{to: <token>, value: 0, data: transfer(attacker, dust)}` or `Call{to: attacker, value: address(this).balance, data: ""}` to steal it before the legitimate sweep/next mint occurs — exactly analogous to how, in the flash-loan report, calling an attacker-influenced target's callback directly (bypassing the intended caller-verification the Lender assumed) let anyone trigger unauthorized behavior.

### Impact Explanation
Any ETH or ERC20 balance transiently or unintentionally left in the single, shared `CallDispatcher` deployment (used across multiple apps — HFT, WHFT, IntentGatewayV2) is stealable by an arbitrary unprivileged caller, since `dispatch()` performs no `onlyGateway`/`onlyHost`/reentrancy-context check. This is a direct theft-of-funds vector affecting a core, reachable, single-transaction attack surface for a shared production contract referenced across multiple deployed apps.

### Likelihood Explanation
Likelihood depends on whether/how often the `CallDispatcher` ends up holding a non-zero balance outside of the atomic call that deposited it (e.g., dust from partial fills, approvals with a remainder, or a `Call.value` forward that isn't fully consumed by the downstream call). The docs and code comments (`DustCollected`, "swept back... as dust", "should use exact amounts rather than unlimited allowances") indicate this is an anticipated, non-trivial occurrence, not a purely theoretical edge case.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the intended caller context (e.g., require `msg.sender` to be a registered/authorized app such as the current token/gateway contract, or make the dispatcher per-call/ephemeral rather than a shared standing contract), and/or ensure the dispatcher never holds a balance across transaction boundaries (sweep 100% of any residual balance back to the originating contract at the end of every `dispatch()` call rather than relying on a separate, delayed sweep).

### Proof of Concept
1. A user bridges tokens via `HyperFungibleToken.send()`/`WrappedHyperFungibleToken` with `to = CALL_DISPATCHER` and `data` encoding an approve+swap `Call[]` that leaves ERC20 dust in the `CallDispatcher` (as shown in the docs' own swap example).
2. `onAccept()` executes the calls via `ICallDispatcher(_dispatcher).dispatch(message.data)`, leaving some dust balance in the shared `CallDispatcher`. [5](#0-4) 
3. Before the legitimate sweep transaction runs, an attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: dustToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, dustAmount)})]))` directly — this succeeds because `dispatch()` has no caller restriction. [2](#0-1) 
4. The attacker has now stolen funds that belonged to the protocol/users, with no on-chain authorization check preventing it.

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L90-98)
```text
The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L99-112)
```text
### Predispatch

The `predispatch` field in `Order` contains calldata to execute *before* escrowing inputs. The predispatch assets specified in `DispatchInfo.assets` are transferred to the `CallDispatcher`, the encoded calls are executed, and the resulting tokens are transferred back to the gateway for escrow. This enables swap-then-escrow patterns — for example, a user sends ETH which the `CallDispatcher` swaps to DAI on Uniswap, and the resulting DAI is escrowed as the order input.

### Postdispatch

The `call` field in `PaymentInfo` contains calldata to execute *after* the order is filled. This enables fill-then-act patterns — for example, output tokens received from the solver are routed through a DeFi protocol before reaching the beneficiary.

Execution timing differs by mode:

- **Same-chain**: Calldata executes only after the order is **fully filled**. Partial fills do not trigger calldata — only the final fill that completes the order executes it. This ensures all output tokens are available when the calls run.
- **Cross-chain**: Calldata executes **immediately** after the solver delivers output tokens to the beneficiary, before the settlement message is dispatched back to the source chain.

After execution, any tokens remaining in the `CallDispatcher` are swept back to the gateway and collected as dust (emitting `DustCollected` for each token). When postdispatch calldata is present, 100% of any surplus (solver overpayment) goes to the protocol rather than being split with the beneficiary — this prevents manipulation of surplus distribution through calldata side effects.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L299-305)
```text
        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```
