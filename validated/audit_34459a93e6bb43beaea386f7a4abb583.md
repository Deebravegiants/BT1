### Title
Unauthenticated `CallDispatcher.dispatch()` allows anyone to permissionlessly drain residual token/native balances routed through the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` executes an arbitrary attacker-supplied `Call[]` against the dispatcher's own balance with no caller restriction. Multiple production apps (`IntentGatewayV2` predispatch/postdispatch, `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata-delivery on `onAccept`) route real user funds (minted tokens, unlocked/predispatch assets, ETH) through this single shared contract instance and rely on the encoded calls consuming the *entire* amount deposited. Any amount left over after those calls execute — the same "operate on the whole balance instead of the specific amount owed" bug class as the referenced report — sits exposed at a well-known, permissionless contract address that anyone can drain with a single `dispatch()` call.

### Finding Description
`CallDispatcher.dispatch()` has no access control at all: [1](#0-0) 

It simply decodes an ABI-encoded `Call[]` and executes each call from its own balance/context (native value transfer + arbitrary calldata). Anyone — not just the app that just funded it — can call this function directly.

Several apps route user-owned assets through this exact same shared dispatcher and assume the encoded calls will consume everything that was deposited:

1. `HyperFungibleToken.onAccept` mints the bridged `amount` to `message.to`. Per the project's own documentation, the recommended calldata-execution pattern sets `to` to the `CallDispatcher` address so that the minted tokens land there before `dispatch(message.data)` is invoked: [2](#0-1) [3](#0-2) 

Unlike `IntentGatewayV2`, this `onAccept` path performs **no sweep-back** after `dispatch()` returns — whatever the encoded `Call[]` does not fully consume (rounding remainders, `swapETHForExactTokens`-style calls that leave the surplus behind, or calldata that only spends part of the minted amount) is permanently left at the `CallDispatcher` address.

2. `IntentGatewayV2.placeOrder`'s predispatch flow and `IntentsBase._execute`'s postdispatch flow route escrowed/output assets through the same `CallDispatcher`, and explicitly sweep back "the entire balance" of the dispatcher rather than the specific amount the order actually needed: [4](#0-3) [5](#0-4) 

Because these sweep calls are themselves just `dispatch()` invocations, and `dispatch()` is unauthenticated, there is no guarantee that the funds present at the `CallDispatcher` when a sweep call executes actually belong to the party that just deposited them — any value sitting there (e.g., dust left by a different app's incomplete consumption, or a still-pending call in a different flow) is fair game to whichever caller reaches `dispatch()` first with a transfer-out `Call`.

### Impact Explanation
Any residual native ETH or ERC20 balance left at the `CallDispatcher` contract — which is explicitly designed to *temporarily* hold real user funds (minted HFT tokens, unlocked WrappedHFT tokens, intent-gateway predispatch/postdispatch assets) — is stealable by any unprivileged address. This is a direct, permanent loss-of-funds vector: an MEV searcher or bot can watch the `CallDispatcher`'s balance and, whenever it becomes non-zero (due to imperfect consumption by the encoded `Call[]`, e.g. slippage-bounded swaps, partial-amount calls, or a revert-free but partial execution), immediately call `dispatch()` with a `Call` that transfers the token/ETH to itself before the legitimate app's own sweep (if any) or a future delivery gets a chance to claim it.

### Likelihood Explanation
The `CallDispatcher` is a single, well-known, publicly documented contract address per chain (listed on the "contract addresses" page) used by multiple apps. The documented usage pattern for `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution explicitly directs integrators to mint/unlock funds directly to the `CallDispatcher` address, and that path has no sweep-back logic at all, so leftover value is essentially guaranteed whenever the destination call doesn't consume exactly 100% of the delivered amount (e.g., exact-output swaps, which by design leave the unused input as leftover). Any relayer, solver, or ordinary bot monitoring `CallDispatcher`'s token/ETH balances can exploit this with a single unauthenticated transaction, with no special privileges required.

### Recommendation
Restrict `CallDispatcher.dispatch()` to authorized callers (e.g., an allow-list of registered gateway/app contracts, or per-call ownership accounting), or redesign the flow so that funds are never left at a shared, permissionless contract between the funding step and the consuming step. At minimum:
- Add caller authorization to `dispatch()` (e.g., `onlyAuthorizedCaller` modifier restricted to registered apps).
- For `HyperFungibleToken`/`WrappedHyperFungibleToken`, add an explicit sweep-back step (mirroring `IntentGatewayV2`) that returns any un-consumed residual balance to the intended beneficiary rather than leaving it at the dispatcher indefinitely.
- Consider making `CallDispatcher` per-call/per-order scoped (e.g., ephemeral clones or a balance-diff-based transfer restricted to the invoking contract) so leftover value cannot be claimed by unrelated third parties.

### Proof of Concept
1. A relayer delivers an HFT/WrappedHFT cross-chain message whose `data` field routes minted/unlocked tokens to the `CallDispatcher` and performs a `swapETHForExactTokens`-style call that only consumes part of the delivered amount (perfectly legal calldata a sender can construct, or simply calldata that under-spends due to price movement/slippage bounds).
2. `onAccept` mints/unlocks the full `amount` to the `CallDispatcher`, then calls `ICallDispatcher(_dispatcher).dispatch(message.data)`; the encoded call only spends part of the balance, leaving the remainder sitting at the dispatcher (no sweep-back exists in this code path).
3. Any third party observes the residual ERC20/ETH balance at the known `CallDispatcher` address and submits a transaction calling `CallDispatcher.dispatch()` directly with `Call[] = [{to: token, value: 0, data: transfer(attacker, balance)}]` (or, for ETH, `{to: attacker, value: balance, data: ""}`).
4. `dispatch()` executes without any authorization check, transferring the residual funds to the attacker — funds that belonged to the legitimate recipient of the bridged transfer.

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
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

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L190-201)
```text
IHyperFungibleToken(address(wrapper)).send{value: nativeFee}(
    IHyperFungibleToken.SendParams({
        dest: StateMachine.evm(1),
        // unlock to the CallDispatcher so it receives the unwrapped ETH
        to: abi.encodePacked(CALL_DISPATCHER),
        amount: amount,
        timeout: 3600,
        relayerFee: relayerFee,
        data: abi.encode(calls)
    })
);
```
```

**File:** evm/src/apps/IntentGatewayV2.sol (L268-282)
```text
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L507-528)
```text
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
