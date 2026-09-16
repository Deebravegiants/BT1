### Title
Unrestricted `CallDispatcher.dispatch()` allows any caller to drain funds transiently or accidentally held by the shared dispatcher contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, permissionless, chain-wide singleton used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` to execute arbitrary attacker/relayer-supplied `Call[]` payloads that arrive inside ISMP messages and cross-chain orders. Its `dispatch()` function has **no caller restriction whatsoever** — no `onlyHost`, no allow-list of the apps that are supposed to use it, and no reentrancy guard — while the contract also accepts arbitrary ETH via `receive()`.

### Finding Description
`CallDispatcher.dispatch()` decodes a `Call[]` and blindly forwards `to.call{value: call.value}(call.data)` for every entry, using the dispatcher's own balance: [1](#0-0) 

There is no check that `msg.sender` is one of the trusted apps that are meant to invoke it (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`/`IntentsBase`). Those apps rely on the dispatcher only as a transient custody/execution point — assets are pushed into it immediately before `dispatch()` is called and swept back out in the same call: [2](#0-1) [3](#0-2) 

Because `dispatch()` is a completely public entry point on a shared, permanently-deployed contract, **anyone** — not just the ISMP host-authorized apps — can call it directly with a crafted `Call[]` that instructs the dispatcher to move out whatever ETH/ERC20 balance it happens to be holding at that moment (dust left over from a partial sweep, ETH sent directly via the open `receive()`, or any token mistakenly/legitimately transferred to the dispatcher address by a relayer/filler before the intended `dispatch()` call executes). The dispatcher itself performs no bookkeeping of "whose funds are these" — it is a bare call-forwarder, so whoever calls `dispatch()` first with the right `Call[]` gets to redirect that balance to an address of their choosing.

This mirrors the IoTDB bug class (CWE-94/insufficiently restricted execution of externally-influenced operations): a component designed to be used only by a privileged/trusted caller executes attacker-controlled instructions because the caller is not actually verified, letting an unprivileged party trigger operations (arbitrary calls funded by the dispatcher's balance) that were only ever meant to be reachable through the vetted app flows.

### Impact Explanation
Any ETH or ERC20 balance transiently or accidentally resident on the shared `CallDispatcher` — across `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2`/`IntentsBase` deployments that all reuse the same dispatcher address — can be swept to an attacker-chosen address by anyone calling `dispatch()` directly, since the function performs no authorization check. This is a direct theft-of-funds primitive on a component that custodies user/protocol assets (escrowed order inputs, HFT calldata-execution transfers) during cross-chain message and intent-order processing.

### Likelihood Explanation
Reachable from a single, ordinary unprivileged call — literally `CallDispatcher.dispatch(...)` — no proof, no consensus verification, and no relayer/administrative privilege is required. Exploitability depends on the dispatcher holding a non-zero balance at the moment of the call (e.g., ETH sent directly via `receive()`, dust from a partially-swept multi-asset order, or a balance left mid-flight by a reentrant call from an attacker-controlled `order.predispatch.call`/`message.data` target that the app flows already execute via this same unrestricted `dispatch()`).

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allow-list (the specific `HyperFungibleToken`/`WrappedHyperFungibleToken`/`IntentGatewayV2` instances authorized to use it, or gate via the ISMP host), add a reentrancy guard, and avoid leaving the contract permanently payable/holding residual balances between calls — e.g., require callers to pass and validate the exact assets they are entitled to move, or make the dispatcher app-scoped/ephemeral instead of a shared singleton with an open `receive()`.

### Proof of Concept
1. Wait for (or induce via a crafted order/message that reenters) any non-zero ETH or ERC20 balance to exist on the shared `CallDispatcher` address (e.g., send ETH directly to it — `receive()` accepts unconditionally).
2. Call `CallDispatcher.dispatch(abi.encode([Call({to: <token_or_target>, value: <balance>, data: <transfer-to-attacker calldata>})]))` directly from any EOA.
3. Since `dispatch()` performs no `msg.sender` check, the call succeeds and the dispatcher's balance is forwarded to the attacker-controlled target, per [4](#0-3) .

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L39-62)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-520)
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
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-313)
```text
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
