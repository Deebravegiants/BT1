### Title
Cross-contract reentrancy via the unguarded, shared `CallDispatcher` singleton allows theft of escrowed order funds during `_execute` dust-sweeping - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2` and `HyperFungibleToken`/`WrappedHyperFungibleToken` all route arbitrary, attacker/user-supplied calldata through one shared, access-control-free `CallDispatcher` contract to compose swap/stake/deposit side-effects. `IntentsBase._execute()` sweeps *whatever token/native balance is currently sitting on the dispatcher* into the calling gateway's own accounting as "dust" — with no per-call balance snapshot and no protection against the dispatcher being used concurrently by a different, unrelated in-flight order. This is the same root-cause shape as the reported `WithdrawalRequestManager` bug: a single shared resource used by multiple mutually-untrusted, equally-privileged callers, where balance-based accounting after an external call is trusted to be attributable solely to the current caller.

### Finding Description
`IntentGatewayV2.fillOrder` and `placeOrder` are each protected by `nonReentrant` (`ReentrancyGuardTransient`), but that guard only protects re-entry into *that specific contract instance* — EIP-1153 transient storage is scoped per contract address. [1](#0-0) [2](#0-1) 

The `CallDispatcher` that both `placeOrder`'s predispatch flow and `fillOrder`'s postdispatch flow (`_execute`) route calls through is a completely permissionless, stateless singleton with no access control and no reentrancy guard of its own — anyone, or any nested call, can invoke `dispatch()` directly: [3](#0-2) 

Crucially, `_execute()` (invoked from `_fillSameChain`/`_fillCrossChain` after delivering outputs) does **not** snapshot the dispatcher's balance before dispatching `order.output.call`; it simply sweeps whatever balance the dispatcher happens to hold at that moment and books it as `DustCollected`: [4](#0-3) 

Because `order.output.call` is an arbitrary `Call[]` dispatched with no restriction on target, it can itself target *any* contract, including a call to `fillOrder`/`placeOrder` on a **second** `IntentGatewayV2` deployment (or `HyperFungibleToken.onAccept`) that shares the exact same `CallDispatcher` address (a documented, intended design — the dispatcher is deployed once per chain and reused across apps): [5](#0-4) [6](#0-5) 

Since the nested call executes as a *different contract instance's* `nonReentrant` lock (or none, in `CallDispatcher`'s case), it is not blocked, and any token balance the nested call causes to land on the shared `CallDispatcher` — e.g. an unrelated victim order's escrowed input tokens released to `msg.sender == CallDispatcher` by that nested `_withdraw`/`fillOrder` call — is present on the dispatcher at the moment the *outer* call's `_execute()` performs its unconditional "sweep everything on the dispatcher" pass, and gets misattributed as the attacker's own order's dust.

### Impact Explanation
An attacker who crafts an order with `output.call` targeting a call into a second gateway/HFT deployment sharing the same `CallDispatcher` can cause escrowed tokens belonging to an unrelated, legitimate order to be routed through the shared dispatcher and then swept into the attacker's own order's dust accounting during `_execute`, resulting in theft of other users'/solvers' escrowed funds. This is a direct, unbacked-value-transfer/theft-of-funds impact reachable from a single attacker-submitted `fillOrder` transaction, matching the report's "theft via shared unprotected resource with naive balance-delta accounting" bug class.

### Likelihood Explanation
Requires: (1) an attacker-controlled order with attacker-chosen `output.call`, which any user can construct via `placeOrder`; (2) more than one app instance (two `IntentGatewayV2` deployments, or a gateway plus an HFT/WHFT) configured to share one `CallDispatcher` address, which is the explicitly documented deployment pattern; and (3) a concurrently reachable second flow whose token movement passes through the shared dispatcher within the nested call. This is non-trivial to engineer precisely but does not require any privileged role, price manipulation, or governance compromise — only careful sequencing of calldata the attacker fully controls, which is the same "moderate but concretely reachable" likelihood profile as the original `WithdrawalRequestManager` report.

### Recommendation
- Add `nonReentrant`/a shared lock to `CallDispatcher.dispatch()` itself so no nested `dispatch()` call can execute while an outer `dispatch()` call for a different order/app is in flight on the same dispatcher instance.
- In `IntentsBase._execute()`, snapshot the dispatcher's balance for each output token/native asset *before* calling `ICallDispatcher(dispatcher).dispatch(order.output.call)` and sweep only the delta (mirroring the pattern already used correctly in `placeOrder`'s predispatch flow), rather than sweeping the dispatcher's entire current balance unconditionally.
- Consider giving each order/app a dedicated, non-shared dispatcher instance (or a dispatcher that tracks per-caller escrow) rather than a single shared, permissionless singleton reused across independent apps and order flows.

### Proof of Concept
1. Deploy two `IntentGatewayV2` proxies, `G1` and `G2`, both configured with the same `_params.dispatcher = D` (a single `CallDispatcher`), matching the documented shared-dispatcher deployment pattern.
2. A victim places a legitimate order `V` on `G2` with input token `T` escrowed, no `output.call`.
3. Attacker places an order `X` on `G1` whose `output.assets` include token `T'` and whose `output.call` is a `Call[]` encoding a call to `G2.fillOrder(V, optionsV)`, funded from tokens the attacker's own order X flow has just caused to land temporarily on `D` (via `X`'s own predispatch/output token handling).
4. Attacker (or any solver) calls `fillOrder(X, optionsX)` on `G1`:
   - `G1._fillSameChain`/`_fillCrossChain` delivers `X`'s outputs, then calls `_execute(X, ...)`.
   - `_execute` calls `D.dispatch(X.output.call)`, which nested-calls `G2.fillOrder(V, optionsV)`.
   - `G2.fillOrder` executes fully (its own `nonReentrant` lock is independent of `G1`'s), delivers `V`'s outputs, and releases `V`'s escrowed input token `T` to `msg.sender == D` via `_withdraw`.
   - Control returns to `G1._execute`, which now observes `D`'s balance of token `T` (deposited by the nested `G2.fillOrder` call) and sweeps it entirely into `G1`'s `DustCollected` accounting for order `X`, even though it rightfully belongs to the flow that just filled order `V`.
5. Net effect: escrowed funds intended for order `V`'s solver/beneficiary are captured by attacker's order `X` on `G1` as "dust", without a snapshot/delta check ever having isolated the two flows on the shared dispatcher.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
```

**File:** evm/src/apps/IntentGatewayV2.sol (L443-443)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-528)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L90-98)
```text
The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L355-357)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```
