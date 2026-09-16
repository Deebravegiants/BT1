### Title
Order creator controls `output.assets` token list swept at full dispatcher balance in `_execute`, letting arbitrary/unrelated tokens held by the shared CallDispatcher be pulled into the gateway - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
The Tempus bug let a caller supply an arbitrary/fake AMM contract whose return values (`ammTokens`, `mintedShares`) the controller trusted blindly, then used those trusted-but-forged values to transfer whatever ERC20 balance the controller held to `msg.sender`. The closest reachable analog in this codebase is `IntentGatewayV2`'s `_execute()` sweep logic, which is driven by attacker-supplied order fields (`order.output.assets[i].token` and `order.output.call`) and sweeps the *entire* `balanceOf` of the shared `_params.dispatcher` contract for whatever token address the order creator names — without tying the swept amount to anything the order actually committed to or escrowed.

### Finding Description
`placeOrder` lets any caller freely choose `order.output.assets` (arbitrary token addresses/amounts) and `order.output.call` (arbitrary calldata to be executed by the shared `CallDispatcher`) [1](#0-0) . On a full fill, `_fillSameChain` calls `_execute(order, outputsLen)` [2](#0-1) .

`_execute` first dispatches the order's arbitrary `output.call` through the single shared `_params.dispatcher`, then — for every token address the order lists in `output.assets` — reads `IERC20(token).balanceOf(dispatcher)` and sweeps the *entire* balance back to the gateway, with no check that this balance corresponds to anything the order itself produced or that the token/amount was validated against an allowlist: [3](#0-2) 

Because `token` in this loop is `address(uint160(uint256(order.output.assets[i].token)))` — fully attacker-chosen — and the swept amount is the dispatcher's live `balanceOf`, not a value computed from escrow accounting, the same structural flaw as the Tempus finding is present: an untrusted, caller-supplied address is used to compute a value (`balance`) that then drives an unconditional token transfer, exactly mirroring how TempusController trusted a caller-supplied `tempusAMM`'s return values to compute `mintedShares - sharesUsed[0]` for a transfer.

### Impact Explanation
If the shared `CallDispatcher` ever holds a balance of any ERC20 token at the moment `_execute` runs — from its own `predispatch`/`output.call` execution in the same transaction, from a prior partially-consumed approval, or from any other in-flight balance — an order creator can name that token in `output.assets` and have the full balance pulled into the gateway during the fill's `_execute` sweep, unconditional on whether that balance has anything to do with the order being filled. This mirrors the Tempus root cause (trusting attacker-supplied contract/token addresses to compute a transfer amount) and could result in loss of funds routed through the dispatcher for unrelated purposes.

### Likelihood Explanation
Reachability requires: (1) placing/filling an order whose `output.call` triggers the dispatcher to (even transiently) hold or interact with a token, and (2) the `output.assets` list naming that token. Both are fully within a single unprivileged caller's control (`placeOrder`/`fillOrder`), the same "single dispatched request" reachability class as the Tempus PoC. I was not able to inspect `ICallDispatcher`'s concrete implementation to confirm whether it can be induced to hold third-party balances (e.g., via stale approvals from other orders' `predispatch` calls), so the exact severity of what tokens can be captured this way is not fully verified from the code available.

### Recommendation
Do not sweep by trusting `balanceOf(dispatcher)` for an order-supplied token list. Instead, track and sweep only the specific amounts the dispatcher is expected to return for *this* order's own predispatch/output execution (as is already done correctly elsewhere in `placeOrder`'s predispatch balance-diffing logic), and/or restrict `_execute`'s sweep to tokens already referenced by the order's own inputs/outputs, never an arbitrary caller-chosen address whose balance is read and moved unconditionally.

### Proof of Concept
1. Order creator crafts `order.output.call` that causes the shared dispatcher to (even momentarily) hold a balance of `TokenX` (e.g., leveraging a stale allowance or leftover balance from the dispatcher's normal operation).
2. Order creator lists `TokenX` in `order.output.assets`.
3. On `fillOrder` → `_fillSameChain` → `_execute`, the contract reads `IERC20(TokenX).balanceOf(dispatcher)` and sweeps 100% of it into the gateway via `ICallDispatcher(dispatcher).dispatch(...)` [4](#0-3) , with no verification the amount belongs to this order.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-227)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L131-133)
```text
        if (isFullyFilled) {
            _execute(order, outputsLen);
            emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: escrowedInputs});
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
