### Title
Stale unlimited-allowance approvals on the shared `CallDispatcher` let an attacker drain any other order's or bridge message's temporarily-held tokens - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher` is a single, shared, stateless "dumb executor" contract used by every `IntentGatewayV2`/`IntentsBase` order (predispatch and postdispatch calldata) and by every `HyperFungibleToken`/`WrappedHyperFungibleToken` cross-chain message with a non-empty `data` field. Any unprivileged caller can embed an arbitrary `Call[]` that includes `token.approve(attacker, type(uint256).max)`, executed with `CallDispatcher` as `msg.sender`. `dispatch()` never revokes or resets any approval it grants, so the allowance persists indefinitely in that ERC20's storage, keyed to the `CallDispatcher` address as owner. Because the same `CallDispatcher` instance later transiently holds tokens belonging to unrelated orders/messages (during predispatch asset transfer, postdispatch output delivery, or HFT calldata execution), the attacker's leftover approval lets them steal those tokens via a plain `transferFrom(dispatcher, attacker, amount)` call, front-run against the honest transaction's own sweep-back step.

### Finding Description
`CallDispatcher.dispatch()` blindly executes attacker-controlled `Call[]` entries with no restriction on target or approval-clearing: [1](#0-0) 

Any order placer can set `order.predispatch.call` to include an ERC20 `approve` call to an attacker address, and `IntentGatewayV2.placeOrder` transfers `predispatch.assets` to the dispatcher and then executes that attacker-supplied calldata as the dispatcher itself: [2](#0-1) 

The same shared dispatcher is also invoked for postdispatch output calldata (`_execute`), where output tokens are delivered to the dispatcher, calls run, and only afterward are leftover balances swept back: [3](#0-2) 

And it is invoked identically for `HyperFungibleToken`/`WrappedHyperFungibleToken` incoming bridged messages carrying a `data` payload — tokens are minted/unlocked, then the dispatcher executes the attacker-influenced calldata: [4](#0-3) 

None of these call sites reset or revoke approvals the dispatcher may have previously granted to third parties. Because `CallDispatcher` is a single per-chain deployment shared across every IntentGateway order and every HFT/WrappedHFT bridge message (its address is fixed and documented per chain), an approval created by one (malicious) order's calldata is not scoped to that order — it is a permanent grant from the dispatcher's address. Any later, unrelated order or bridge delivery that causes the dispatcher to transiently hold the same ERC20 (predispatch asset staging, postdispatch output delivery before sweep, or HFT mint-then-dispatch) exposes that balance to the attacker's dangling `transferFrom` allowance. Because the protocol's own documentation only warns callers to "use exact amounts rather than unlimited allowances" for the calls they submit — it never restores the invariant that a spender authorized during one interaction cannot reach through unrelated future interactions — this mirrors the CouncilMember bug class: an approval that outlives the transaction/session it was intended for and lets an unrelated party's assets be swept by a stale spender.

### Impact Explanation
This is a direct theft-of-funds vector reachable by any unprivileged intent-order placer or bridge sender: no governance or admin privilege is required to set up the malicious approval, and exploitation only requires observing (or timing against) a pending predispatch/postdispatch transaction that will route the same token through the shared dispatcher. Funds belonging to legitimate users/solvers/bridged-token recipients can be permanently stolen from the shared dispatcher's transient balance. This satisfies "concrete theft of funds" and reaches the intents escrow / token bridge mint-unlock paths explicitly in scope.

### Likelihood Explanation
Likelihood is meaningful but conditional: the attacker must (a) place one order (or trigger one bridge message) with malicious calldata to plant the approval, and (b) win a race to call `transferFrom` before the dispatcher's sweep-back logic drains the balance in a subsequent, unrelated transaction that happens to move the same ERC20 through the dispatcher. Given the dispatcher is a single shared address used continuously by all IntentGateway orders and all HFT deployments on a chain, and given predispatch specifically creates a visible mempool window (assets sent to dispatcher in one call, `dispatch()` in a following step of the same transaction, but the target token balance sits at the dispatcher address before that step executes and is observable pre-confirmation), a motivated MEV-capable attacker can realistically front-run to catch that window repeatedly across many orders touching popular tokens (USDC, DAI, etc.).

### Recommendation
- Have `CallDispatcher.dispatch()` (or the calling contracts) explicitly reset any approvals it granted to zero immediately after each `dispatch()` call for every token address touched by the call batch, or
- Deploy a fresh, order-scoped/message-scoped dispatcher instance (e.g., via minimal proxy/clone) per call rather than sharing one persistent address across all orders and bridge messages, eliminating the ability for one interaction's leftover approvals to reach another's transient balance, or
- Disallow `approve`/`increaseAllowance` selectors targeting the dispatcher's own held tokens within `Call[]` entries, forcing token movement through explicit `transfer` calls only.

### Proof of Concept
1. Attacker places (or fills) an `IntentGatewayV2` order whose `predispatch.call` (or `output.call`) is `[{ to: USDC, value: 0, data: approve(attacker, type(uint256).max) }]`. This executes with `CallDispatcher` as `msg.sender`, granting `attacker` an unlimited USDC allowance from the dispatcher — this call requires no special privilege, per `IntentGatewayV2.sol` lines 235-260 / `IntentsBase.sol` lines 498-528.
2. At any later time, a victim places an unrelated order whose `predispatch.assets` includes USDC, which the gateway transfers to `dispatcher` before calling `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`.
3. Attacker observes the victim's pending transaction in the mempool and front-runs with `USDC.transferFrom(dispatcher, attacker, amount)`, draining the victim's staged escrow funds from the dispatcher before the victim's own predispatch call and subsequent sweep executes.
4. The victim's transaction then reverts (insufficient dispatcher balance) or completes with a reduced/zero amount, while the attacker has stolen the USDC that was meant to be escrowed for the victim's order.

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-336)
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

        emit Received({from: message.from, to: beneficiary, source: string(request.source), amount: message.amount});
    }
```
