### Title
Shared `CallDispatcher` accumulates undrained token/ETH dust across unrelated bridge transfers, letting any subsequent sender steal it via unrestricted post-mint calldata - (File: `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`, `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`, `evm/src/utils/CallDispatcher.sol`)

### Summary
`HyperFungibleToken.onAccept` and `WrappedHyperFungibleToken.onAccept` mint/unlock bridged tokens and then forward attacker-controlled `Call[]` calldata to a singleton `CallDispatcher` contract, which executes each call with `to.call{value}(data)` against any target the message's original sender chose — with zero restriction on which token/target can be called, exactly the class of flaw in the WatchPug `arbitraryCall()` report (no check against reusing a shared context to move value that isn't the caller's). Unlike `IntentsBase._execute`, which explicitly sweeps any residual balance left on the `CallDispatcher` back to the gateway after execution, `HyperFungibleToken.onAccept`/`WrappedHyperFungibleToken.onAccept` never sweep dust. Because `CallDispatcher` is a single, shared, stateful contract reused by every HFT/WrappedHFT deployment (and by `IntentGatewayV2`) on a chain, any token or native-ETH residue left behind by one user's imperfect swap calldata sits in the dispatcher's balance indefinitely and can be drained by any later, unrelated sender who crafts calldata targeting that leftover balance.

### Finding Description
`onAccept` mints/unlocks tokens to `beneficiary` and then unconditionally dispatches `message.data` to the shared dispatcher: [1](#0-0) 

`CallDispatcher.dispatch` places no restriction on the call target or calldata beyond requiring the target to have code — it simply forwards value and calldata as itself: [2](#0-1) 

The documentation itself confirms `CallDispatcher` is a shared, chain-wide singleton (listed on the contract-addresses pages) intentionally reused for "transfer-and-swap" composability, and explicitly warns that unlimited approvals left on it are risky "since the dispatcher contract holds tokens temporarily during execution": [3](#0-2) 

Both bridge contracts recommend routing bridged funds directly to the `CallDispatcher` address so the follow-up swap/approve call can spend them: [4](#0-3) 

Crucially, `IntentsBase._execute` — which uses the exact same `CallDispatcher` for post-fill calldata — recognizes this hazard and explicitly sweeps any token/native balance left on the dispatcher back to the gateway after every execution, emitting `DustCollected`: [5](#0-4) 

`HyperFungibleToken.onAccept` and `WrappedHyperFungibleToken.onAccept` have no equivalent sweep step; after `ICallDispatcher(_dispatcher).dispatch(message.data)` returns, execution ends immediately: [6](#0-5) 

Because `message.to`, `message.amount`, and `message.data` (hence the `Call[]` array's targets, values, and calldata) are all chosen by the originating sender on the source chain, any bridge user who mints/unlocks tokens to the `CallDispatcher` and whose follow-up swap/approve calldata doesn't fully consume the delivered amount (partial fill, rounding, slippage-protected swap that reverts on the surplus leg, or simply a bug) leaves that residue sitting in `CallDispatcher`'s ERC-20 balance or native ETH balance. Since `CallDispatcher` is the same contract instance shared by every HFT/WrappedHFT pair (and `IntentGatewayV2`) on that chain, any other, entirely unrelated user can later dispatch their own legitimate cross-chain transfer with `data` crafted as `Call({to: leftoverToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, dispatcher.balance)})` (or the native-ETH equivalent via `Call.value`). Because the dispatcher executes as itself, this call succeeds and sweeps out value that belongs to a stranger's prior transfer — the direct analog of the WatchPug report's core defect: an arbitrary-call primitive with no check preventing it from being aimed at value that isn't the caller's own.

### Impact Explanation
Any accumulated dust (ERC-20 tokens or native ETH) left in the shared `CallDispatcher` by any user's cross-chain transfer becomes permanently stealable by any other unprivileged user who simply crafts their own calldata to target it. This is direct theft of funds that belong to prior, unrelated bridge users, reachable purely via a single self-dispatched `send()` call — no governance, relayer, or consensus compromise is required. Given `CallDispatcher` is a chain-wide singleton reused across HFT, WrappedHFT, and `IntentGatewayV2` deployments, the blast radius spans every app instance sharing that dispatcher address.

### Likelihood Explanation
Likelihood is elevated by the fact that the docs explicitly recommend and demonstrate the "mint/unlock directly to `CALL_DISPATCHER`, then swap" pattern as the standard way to compose calldata execution, meaning dust accumulation via slippage, partial swap failures, or rounding is a realistic and recurring byproduct of normal usage rather than a contrived edge case. The attack itself requires no special access — merely observing the dispatcher's token/ETH balance (public, on-chain) and submitting one more bridge transfer with adversarial calldata.

### Recommendation
Mirror the mitigation already present in `IntentsBase._execute`: after every `ICallDispatcher(_dispatcher).dispatch(message.data)` call in `HyperFungibleToken.onAccept`, `HyperFungibleTokenUpgradeable.onAccept`, `WrappedHyperFungibleToken.onAccept`, and `WrappedHyperFungibleTokenUpgradeable.onAccept`, sweep any residual token/native balance left on the dispatcher back to a safe location (e.g., refund to the intended beneficiary or emit and revert if non-zero, forcing the sender to size calldata precisely) so no state persists on the shared `CallDispatcher` between unrelated transactions.

### Proof of Concept
1. Alice bridges `1000 USDC` via `HyperFungibleToken.send()` with `to = CALL_DISPATCHER` and `data` encoding a swap call that only spends `999.999 USDC` (e.g., due to a fixed `amountIn` miscalculation or a partial-fill router call), per the documented pattern in `docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx:149-162`.
2. `HyperFungibleToken.onAccept` mints `1000 USDC` to `CALL_DISPATCHER`, then `ICallDispatcher(_dispatcher).dispatch(message.data)` runs the swap, leaving `0.001 USDC` stranded on `CallDispatcher` (per `sdk/packages/core/contracts/apps/HyperFungibleToken.sol:301-306`, with no sweep-back).
3. Repeated across many users/transfers, `CallDispatcher`'s USDC balance grows over time.
4. Bob (unprivileged attacker) dispatches his own trivial `send()` with `data` encoding `Call({to: USDC, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, bob, USDC.balanceOf(CALL_DISPATCHER))})`.
5. `CallDispatcher.dispatch` (`evm/src/utils/CallDispatcher.sol:44-62`) executes this unrestricted call as itself, transferring the entire accumulated dust balance — funds belonging to Alice and other prior senders — to Bob.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L300-306)
```text
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L86-98)
```text
## Calldata Execution

Both contracts support optional calldata execution on the destination chain via the `CallDispatcher`. By passing a non-empty `data` field in `SendParams`, the sender can trigger arbitrary contract calls on the destination chain immediately after tokens are minted or unlocked. This enables composable cross-chain workflows like transfer-and-swap (e.g., bridge USDC then swap to WETH via UniswapV2), transfer-and-stake, or transfer-and-deposit into a lending protocol — all in a single cross-chain operation.

The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L487-533)
```text
    /**
     * @dev Executes arbitrary calldata attached to an order's output via the CallDispatcher.
     * After dispatching the calls, any residual token balances left on the dispatcher
     * are swept back to this contract and accounted for as protocol dust.
     *
     * This enables composable order fulfillment — solvers can route through DEXes,
     * lending protocols, or other DeFi primitives as part of filling an order.
     *
     * @param order The order containing the output calldata to execute.
     * @param outputsLen The number of output assets to sweep after execution.
     */
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L322-330)
```text
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
```
