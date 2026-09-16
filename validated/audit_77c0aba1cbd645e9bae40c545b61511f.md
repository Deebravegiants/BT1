### Title
Unauthenticated `CallDispatcher.dispatch()` allows anyone to steal tokens left in the shared dispatcher contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The Axelar report describes an `Executor` that lets *any* caller build a payload that reaches a privileged receiver hook (`executeWithToken`), so tokens that are minted into the executor before the intended call runs can be stolen by a third party because the executor performs no whitelist/authorization check on who may trigger the call. Hyperbridge's `CallDispatcher` — the shared "arbitrary external call" primitive used by both `HyperFungibleToken`/`HyperFungibleTokenUpgradeable` (calldata-execution path) and `IntentGatewayV2` (predispatch/postdispatch) — has the exact same missing-authorization root cause: `dispatch()` is a fully public function with no `msg.sender` check and no destination whitelist, on a contract that is designed to transiently (and, in at least one flow, permanently) hold user funds.

### Finding Description
`CallDispatcher.dispatch()` decodes a `Call[]` and blindly forwards every call, with zero access control: [1](#0-0) 

Nothing restricts who may invoke `dispatch()` — not `onlyOwner`, not a check that `msg.sender` is `HyperFungibleToken`/`IntentGatewayV2`, nothing. The contract also accepts arbitrary ETH via `receive()`: [2](#0-1) 

`HyperFungibleToken.onAccept` mints the bridged amount directly to the `CallDispatcher` address (when the sender sets `to = CallDispatcher`, exactly as documented for the "swap after bridge" pattern) and then forwards the attached calldata to it: [3](#0-2) 

Unlike `IntentGatewayV2`/`IntentsBase._execute`, which explicitly sweeps any residual balance left on the dispatcher back to the gateway after execution: [4](#0-3) 

`HyperFungibleToken.onAccept` has **no sweep-back step** after `ICallDispatcher(_dispatcher).dispatch(message.data)`. Any tokens minted to the dispatcher that are not fully consumed by the attached `Call[]` (e.g. slippage on a swap, an approval for less than the full minted amount, or a call that only spends part of the balance) remain permanently on the `CallDispatcher` contract's balance.

Because `CallDispatcher` is a single, shared, chain-wide singleton (the docs reference "Existing `CallDispatcher` deployments" per chain, used by every `HyperFungibleToken`/`WrappedHyperFungibleToken` instance and by `IntentGatewayV2`), and because `dispatch()` has no gating, **any unprivileged address can call `dispatch()` directly** with a `Call[]` that instructs an ERC20 token held by the dispatcher to `transfer()` its balance to the attacker — sweeping out any dust/leftover funds belonging to a bridge user before the legitimate protocol (or the rightful recipient) can recover them.

This is a structural match to the reported bug class: an "executor"/dispatcher contract that (a) accepts arbitrary external calls, (b) is reachable by an unprivileged party, and (c) is the same contract that receives minted/bridged funds mid-flow, with no whitelist protecting either the call target or the caller.

### Impact Explanation
Concrete theft of user funds: any leftover ERC20 balance stranded on the `CallDispatcher` after a `HyperFungibleToken` calldata-execution delivery (or any stray ETH sent to it via `receive()`) can be swept to an arbitrary attacker-controlled address by anyone who races to call `dispatch()` first. Since the same dispatcher is shared across every deployed `HyperFungibleToken`/`WrappedHyperFungibleToken` instance and `IntentGatewayV2` on a chain, the blast radius covers all apps that route calldata through it. This is High severity per the same rationale as the original Axelar finding — unauthorized fund extraction from a "receiver"/executor contract with no caller whitelist.

### Likelihood Explanation
Any bridge transfer that uses the documented "mint to CallDispatcher then swap" pattern with calldata that does not perfectly consume the entire minted amount (very common with slippage-protected swaps, since `minAmountOut` deliberately leaves some tolerance, or with multi-step `Call[]` sequences that approve rather than transfer the full balance) will leave a nonzero residual balance on the dispatcher. Because `dispatch()` is a public, unauthenticated function, exploitation requires no special privilege or timing beyond monitoring the dispatcher's token balances and calling `dispatch()` — this is straightforward to automate and front-run.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to a whitelist of authorized callers (e.g., only the registered `HyperFungibleToken`/`IntentGatewayV2` instances that were configured with this dispatcher), similar to how the Axelar fix recommended whitelisting callers/targets in the Executor.
- Alternatively, deploy a fresh, single-use `CallDispatcher`-equivalent (ephemeral execution context) per delivery so no balance can ever persist across transactions/callers.
- Add a mandatory sweep-back of any residual balance to the intended recipient at the end of `HyperFungibleToken.onAccept`'s calldata-execution branch, mirroring `IntentsBase._execute`'s dust-sweep logic.

### Proof of Concept
1. Attacker deploys/observes a `HyperFungibleToken` deployment that shares a chain-wide `CallDispatcher` at address `D`.
2. A user bridges tokens with `to = D` and `data` encoding `Call[]` = [`approve(router, amount)`, `swapExactTokensForTokens(amount, minAmountOut, path, recipient, deadline)`]. Because of slippage tolerance, the swap only spends part of the approved amount, leaving `dust` tokens of the bridged asset on `D`.
3. `onAccept` (`sdk/packages/core/contracts/apps/HyperFungibleToken.sol#L292-L313`) completes: `dust` tokens remain on `D`'s balance, with no code path to reclaim them automatically.
4. Attacker calls `CallDispatcher(D).dispatch(abi.encode([Call({to: bridgedToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, dust)})]))` directly — this succeeds because `dispatch()` performs no caller check (`evm/src/utils/CallDispatcher.sol#L44-L62`) — transferring the stranded user funds to the attacker.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-527)
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
```
