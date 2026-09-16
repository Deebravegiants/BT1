## Title
Unrestricted `CallDispatcher.dispatch()` allows anyone to drain any tokens/ETH transiently or residually held by the shared dispatcher contract - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher` is a single, shared, protocol-wide contract used by `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` to execute arbitrary user-supplied `Call[]` payloads while temporarily holding user funds (predispatch/postdispatch assets, unlocked bridge tokens). Its only entrypoint, `dispatch(bytes memory encoded)`, has **no access control whatsoever** — any address can call it directly and instruct the dispatcher to move out any ERC20 or native balance it currently holds, to any destination.

### Finding Description
`CallDispatcher.dispatch()` is declared `external` with zero caller restriction: [1](#0-0) 

This contract is not a per-user, one-off instance — it is a single deployment reused across the whole protocol as the execution/holding point for predispatch and postdispatch calldata in `IntentGatewayV2`: [2](#0-1) 

and for calldata attached to cross-chain token deliveries in `HyperFungibleToken`/`WrappedHyperFungibleToken`: [3](#0-2) 

Both flows only sweep back the *specific* tokens enumerated in the order's `inputs`/`output.assets` list: [4](#0-3) 

Any token or native balance that ends up on the dispatcher outside of that enumerated set — e.g., dust/reward tokens produced as a side effect of a DEX/DeFi route embedded in `predispatch.call`/`output.call`, native ETH sent directly to the dispatcher's `receive()`, or funds left over from a call that partially executes — is never swept and remains sitting on the contract. Because `dispatch()` has no `onlyGateway`/`onlyOwner`/allow-list check, **any unprivileged address can call `CallDispatcher.dispatch()` directly** (bypassing `IntentGatewayV2`/`HyperFungibleToken` entirely) with a `Call[]` that transfers out any ERC20 balance (`IERC20.transfer.selector`) or forwards any native ETH balance the dispatcher currently holds, since the dispatcher itself is `msg.sender`/owner of those funds from the token's perspective.

This mirrors the MetaPoint root cause exactly: a contract that holds user funds during a workflow exposes a public function (there: `approve`, here: `dispatch`) that lets an unrelated caller move all assets the holding contract currently controls, without any check that the caller is the authorized orchestrator.

### Impact Explanation
Any assets (ERC20 dust, unaccounted side-effect tokens, or stray native ETH) sitting on the shared `CallDispatcher` at any point — whether left over from `IntentGatewayV2` predispatch/postdispatch composable calls or from `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution — are permissionlessly stealable by any address in the world. Because the dispatcher is shared across the entire deployment (one instance serving all orders/messages), this is not confined to a single user's funds; it is a standing, protocol-wide unauthorized-drain primitive on whatever the dispatcher happens to hold, satisfying "concrete theft of funds" / "unauthorized app action" reachable from a single unprivileged transaction.

### Likelihood Explanation
Reachability requires no special privilege: `dispatch()` is a bare external function on a publicly known, permanently deployed contract address. Any MEV searcher or attacker can watch the dispatcher's token balances (e.g. via mempool monitoring of `placeOrder`/`fillOrder`/`onAccept` calls that route tokens through it, or DeFi calldata that yields residual tokens) and immediately front-run/back-run with a direct `dispatch()` call sweeping the balance before the legitimate sweep step executes or whenever unaccounted dust accumulates.

### Recommendation
Restrict `CallDispatcher.dispatch()` to an allow-list of authorized callers (the `IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken` instances configured to use it), e.g. via an `onlyAuthorized` modifier checked against a governance-managed mapping, and/or scope each app to its own dedicated `CallDispatcher` instance rather than a shared singleton, so that no unrelated party can ever move funds the dispatcher is holding on behalf of another app/order.

### Proof of Concept
1. Observe (via mempool or on-chain) that `CallDispatcher` at the well-known shared address currently holds a nonzero ERC20 balance (e.g. dust left from a `postdispatch` DeFi route in `IntentGatewayV2._execute`, or a token/ETH sent by mistake to the dispatcher's `receive()`).
2. Call `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]))` directly — no relationship to `IntentGatewayV2` or any order is required.
3. `dispatch()` executes the call because there is no caller check; `token.transfer(attacker, balance)` succeeds because `CallDispatcher` is the token holder, and the funds are now with the attacker.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L241-259)
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-328)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
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
