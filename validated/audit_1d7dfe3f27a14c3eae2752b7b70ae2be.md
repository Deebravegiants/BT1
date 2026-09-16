### Title
Stale ERC20 approvals on the shared `CallDispatcher` let any unprivileged HFT sender or intent filler drain tokens routed through later messages/orders - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, persistent, protocol-wide contract that executes arbitrary `Call[]` sequences supplied by *unprivileged* callers of `HyperFungibleToken`/`WrappedHyperFungibleToken` (`send()`'s `data` field) and `IntentGatewayV2` (`order.output.call` / `predispatch.call`). Because the dispatcher is one shared address used by every bridged message and every filled order, an ERC20 `approve()` call embedded in one attacker-controlled payload leaves a durable allowance from the dispatcher to an attacker-chosen spender. That allowance is not revoked after the dispatch that created it. Any later, unrelated message or order that causes tokens to pass through the same dispatcher address can then be drained via the stale allowance — the same root cause as the ParaSwap AugustusSwapper incident, where an unprivileged caller's arbitrary-callee `simpleSwap` was used to weaponize a stale approval held by the router.

### Finding Description
`CallDispatcher.dispatch()` blindly executes attacker-supplied `Call[]` entries against arbitrary `to` addresses with arbitrary `data`, and never resets any allowance it grants: [1](#0-0) 

Three unprivileged entry points feed attacker-controlled `Call[]` into this single shared contract:

1. `HyperFungibleToken`/`HyperFungibleTokenUpgradeable.onAccept` mints tokens then forwards the *sender-controlled* `message.data` straight to the dispatcher: [2](#0-1) 
The `data` field originates entirely from the caller of `send()` on the source chain — any account can choose it: [3](#0-2) 

2. `IntentsBase._execute` dispatches `order.output.call`, which is filler/order-supplied calldata, to the same dispatcher instance configured in `Params.dispatcher`: [4](#0-3) 

3. The protocol's own documentation confirms the dispatcher persistently holds allowances across unrelated flows and explicitly shifts the burden of preventing this onto the caller rather than enforcing it in code: [5](#0-4) 

Because `CallDispatcher` is one fixed, protocol-configured address (`ConfigOptions.dispatcher` / `Params.dispatcher`) reused by *every* HFT message and *every* IntentGatewayV2 order, an attacker can:
- Send an HFT message (or place/fill an order) whose `Call[]` contains `TOKEN.approve(ATTACKER_SPENDER, MAX_UINT)` (or any large amount), executed by the dispatcher against a legitimate token.
- Wait for any later, unrelated bridged message or order-fill that must temporarily route the same token through the dispatcher (e.g. an order whose output tokens are minted/unlocked to the dispatcher for `approve`+swap composition, per the documented "transfer-and-swap" pattern).
- Call `TOKEN.transferFrom(dispatcher, attacker, amount)` from `ATTACKER_SPENDER` using the stale allowance to steal the tokens belonging to the unrelated flow before the dust-sweep in `_execute` (which only sweeps tokens explicitly listed in that specific order's `output.assets`) or the HFT mint completes.

This is structurally identical to the ParaSwap DAI exploit: a shared, privileged executor (`AugustusSwapper` / `CallDispatcher`) that lets an unprivileged caller inject arbitrary callee/calldata, combined with an allowance left over from an unrelated approval, is later exploited to redirect tokens that a different, legitimate flow deposited into that same privileged address.

### Impact Explanation
Successful exploitation drains tokens that legitimate users/solvers route through the shared `CallDispatcher` during normal cross-chain transfer-and-swap or order-fulfillment composability flows — a concrete theft of bridged/escrowed funds, not merely dust. Any HFT deployment or `IntentGatewayV2` deployment sharing a `CallDispatcher` address is affected, and since the dispatcher is reused by design across all callers, the blast radius covers every user who ever routes tokens through it after a malicious approval has been planted.

### Likelihood Explanation
The attack requires no privileged role: any account can call `HyperFungibleToken.send()` with crafted `data`, or place/fill an `IntentGatewayV2` order with a crafted `output.call`/`predispatch.call`, both of which are core, unprivileged, publicly documented features (the docs even show `approve()` as an example `Call`). The only timing dependency is waiting for a subsequent flow that deposits the targeted token into the dispatcher — a routine occurrence given the dispatcher's advertised "transfer-and-swap" composability use case.

### Recommendation
- Do not allow arbitrary `approve()` targets/spenders to persist on `CallDispatcher`: either (a) require the dispatcher to revoke (`approve(spender, 0)`) any allowance it grants at the end of `dispatch()`, or (b) use a fresh, single-use dispatcher (e.g. minimal proxy/clone) per message/order instead of one shared, long-lived contract.
- Alternatively, restrict `Call[].to` in `CallDispatcher` to a per-message allowlist supplied by the app (HFT/IntentGatewayV2) rather than trusting caller-supplied targets unconditionally.
- Enforce (in code, not just documentation) that any approval created during `dispatch()` cannot outlive the single call, e.g. by wrapping dispatch in a check that all allowances granted within the call are zero afterward.

### Proof of Concept
Conceptual PoC (cannot be fully instantiated without deployment addresses, but the mechanism is directly testable against the existing Foundry harness):
1. Attacker calls `HyperFungibleToken.send()` (or places/fills an `IntentGatewayV2` order) with `data`/`output.call` encoding `Call{ to: TOKEN, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, ATTACKER_SPENDER, type(uint256).max) }`. This executes via `CallDispatcher.dispatch()`, leaving `TOKEN.allowance(dispatcher, ATTACKER_SPENDER) == max`.
2. A legitimate, unrelated victim later fills an order (or receives an HFT transfer) whose `Call[]` mints/unlocks/transfers `TOKEN` to the same `dispatcher` address as part of a swap-composition flow (per the documented pattern of setting `to: CALL_DISPATCHER`).
3. Attacker (via `ATTACKER_SPENDER`) calls `TOKEN.transferFrom(dispatcher, attacker, victimAmount)` using the still-valid allowance from step 1, draining the victim's tokens before/while they sit in the dispatcher.

This mirrors `testSurplusWithCalldataGoesToProtocol`/the partial-fill residual-allowance test already present in the repo's own test suite, which independently confirms that `approve()` calls dispatched through the CallDispatcher leave measurable residual allowances rather than being reset: [6](#0-5)

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L51-67)
```text
    struct SendParams {
        /// @notice Destination chain identifier (e.g., StateMachine.evm(1))
        bytes dest;
        /// @notice Recipient account on the destination chain
        bytes to;
        /// @notice Amount of tokens to send
        uint256 amount;
        /// @notice Timeout duration in seconds for the cross-chain message
        uint64 timeout;
        /// @notice Fee paid to relayers for message delivery
        uint256 relayerFee;
        /**
         * @notice Optional calldata to execute on the destination chain via CallDispatcher.
         * Should be an abi-encoded Call[] array.
         */
        bytes data;
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1711-1725)
```text
        dai.approve(address(intentGateway), outputAmount);
        TokenInfo[] memory outputs2 = new TokenInfo[](1);
        outputs2[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: outputAmount});
        intentGateway.fillOrder(
            order, FillOptions({relayerFee: 0, nativeDispatchFee: 0, validUntil: 0, outputs: outputs2})
        );
        vm.stopPrank();

        // Allowance should now be 1 (calldata executed)
        assertEq(
            dai.allowance(address(intentGateway.params().dispatcher), address(intentGateway)),
            1,
            "Calldata should execute after full fill"
        );
    }
```
