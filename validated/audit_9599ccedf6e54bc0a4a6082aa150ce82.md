### Title
Unauthenticated `CallDispatcher.dispatch()` allows theft of any funds/approvals transiently held by the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` executes an attacker-supplied array of arbitrary `(to, value, data)` calls with no caller restriction whatsoever. The contract is a single shared singleton reused across `HyperFungibleToken`, `WrappedHyperFungibleToken`, `WrappedHyperFungibleTokenUpgradeable`, and `IntentGatewayV2`/`IntentsBase`, each of which transiently routes tokens, ETH, and ERC20 approvals through it as part of `onAccept` calldata execution and order predispatch/postdispatch flows. Because `dispatch()` has no `onlyHost`/`onlyCaller` gate (unlike `onAccept`, which is protected by `onlyHost`), any unprivileged actor can call it directly, in an unrelated transaction, to sweep out any balance or standing ERC20 allowance the dispatcher happens to be holding at that moment.

### Finding Description
`CallDispatcher.dispatch` is declared as a plain `external` function with no modifier: [1](#0-0) 

Compare this to every legitimate caller of `dispatch()`, all of which are protected on their own inbound side (`onlyHost`) but call into the dispatcher without the dispatcher itself verifying who is calling it: [2](#0-1) [3](#0-2) [4](#0-3) 

The contract also accepts ETH via a permissionless `receive()`: [5](#0-4) 

The project's own documentation acknowledges the dispatcher transiently holds funds and even warns callers to use exact-amount approvals rather than unlimited ones "since the dispatcher contract holds tokens temporarily during execution": [6](#0-5) 

Because `dispatch()` is reachable by anyone at any time (not only mid-flight inside a legitimate `onAccept`/`fillOrder` transaction), any of the following residual state is stealable by a completely unprivileged caller:
- Native ETH sent via `receive()` that hasn't yet been consumed by a queued `Call[]`.
- ERC20 tokens minted/unlocked/transferred to the dispatcher address as the `to` recipient of a cross-chain transfer (per the documented pattern of setting `to` = `CALL_DISPATCHER` so downstream calls can spend the funds), if the follow-up sweep/dispatch does not execute atomically in the same transaction or leaves dust.
- Outstanding ERC20 `approve()` allowances granted by a prior `Call[]` batch (e.g., `approve(DEST_TOKEN, ROUTER, amount)` from the HFT/IntentGateway examples) that were not fully consumed by the paired swap call in the same batch.

An attacker simply calls `CallDispatcher.dispatch(abi.encode(maliciousCalls))` directly with a `Call` that transfers out any token balance the dispatcher currently holds, or that calls `transferFrom`/`transfer` against an outstanding allowance, redirecting funds to themselves.

### Impact Explanation
This is a theft-of-funds vector on a contract that is documented and designed to transiently custody bridged tokens and native ETH across multiple production apps (`HyperFungibleToken`, `WrappedHyperFungibleToken(Upgradeable)`, `IntentGatewayV2`/`IntentsBase`). Any value left in the shared `CallDispatcher` — dust, un-swept transfers, or un-consumed approvals — is fully drainable by an arbitrary unprivileged third party, since `dispatch()` performs no origin/caller validation before executing attacker-controlled external calls with the dispatcher's own token balance and allowances.

### Likelihood Explanation
Reaching this path requires no privilege, proof, relayer role, or governance access — a single direct call to the publicly deployed, permissionless `dispatch()` function is sufficient. The only precondition is that the shared dispatcher singleton is holding exploitable balance/allowance at call time, which is the normal, documented operating mode of the contract (tokens/ETH are routed through it as part of every calldata-bearing cross-chain transfer or intent fill).

### Recommendation
Restrict `CallDispatcher.dispatch()` to a known, per-caller-scoped invocation model: e.g., require `msg.sender` to be one of the registered apps/hosts that are expected to route calls through it, or replace the shared singleton pattern with a fresh, single-use dispatcher (e.g., deployed via `CREATE2`/minimal proxy per call) so no balance or approval can ever persist between unrelated transactions. At minimum, ensure every caller (`onAccept`, `_execute`, predispatch/postdispatch) fully sweeps and revokes any approvals granted to the dispatcher within the same atomic call, and add a reentrancy/self-only guard so `dispatch()` cannot be invoked outside of the intended call chain.

### Proof of Concept
1. A legitimate cross-chain transfer sets `to = CALL_DISPATCHER` and includes calldata that `approve()`s a DEX router for `amount` tokens (per the documented transfer-and-swap pattern) but the paired swap call consumes less than the full approved amount, or reverts after the approval succeeds due to slippage.
2. The `CallDispatcher` singleton is left holding a non-zero ERC20 allowance to the router (or leftover token balance) after the transaction completes.
3. An attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: transferFrom(dispatcher, attacker, allowance)})]))` directly — no `onlyHost` or caller check exists on `dispatch()` — draining the residual allowance/balance to their own address.

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-306)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** evm/src/apps/IntentGatewayV2.sol (L241-258)
```text
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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
