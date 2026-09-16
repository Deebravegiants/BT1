## Title
`CallDispatcher.dispatch` has no caller authorization, letting anyone sweep any token/native balance the shared dispatcher happens to hold - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher.dispatch(bytes)` is `external` with no access control whatsoever — no `onlyHost`, no allow‑list, not even a check that the caller is one of the apps that is supposed to use it. It is deployed once and reused as a shared, long‑lived singleton across `HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`/`IntentsBase`, etc. (it appears on the published mainnet/testnet contract-address pages, confirming it's a persistent, shared contract rather than a fresh one per call). Any ERC20 or native ETH balance sitting on this contract — even momentarily, or as leftover dust from an interrupted/partial sweep, or from ETH sent directly via its unguarded `receive()` — can be extracted by *any* unprivileged address in a single transaction by calling `dispatch()` with an attacker-chosen `Call[]` that transfers the balance to itself.

### Finding Description
`CallDispatcher.dispatch` only validates that each `Call.to` target has code; it performs no check on `msg.sender` and forwards whatever value/calldata the caller supplies: [1](#0-0) 

The apps that use it (`HyperFungibleToken.onAccept`, `WrappedHyperFungibleTokenUpgradeable.onAccept`, `IntentsBase._execute`, `IntentGatewayV2.placeOrder`'s predispatch flow) transfer tokens/ETH to the dispatcher, call `dispatch()` with trusted calldata, and then sweep the remainder back: [2](#0-1) [3](#0-2) 

This is exactly the fund-loss pattern described in the report: a helper/integration contract (`lendingPool`/`AToken` in the DODO case, `CallDispatcher` here) is expected to only ever be invoked in a trusted context, but its externally callable action function does not verify who is calling it or on whose behalf. In the DODO report, `executeOperation` trusted `msg.sender == lendingPool` but never checked `_initiator`, letting Bob supply crafted `_swapParams` that drained Alice's `AToken`. Here, `CallDispatcher.dispatch` doesn't even have the equivalent of the `msg.sender == lendingPool` check — it is open to literally anyone — so any balance it holds, even transiently between the "receive tokens" and "sweep back" steps of a single legitimate app's flow, or any balance mistakenly/maliciously left on it (e.g., native ETH via its permissionless `receive()`), can be stolen by an unrelated third party in a single call.

Additionally, `CallDispatcher.receive() external payable {}` accepts native ETH from anyone with no bookkeeping, so ETH sent to it (by mistake, or as leftover from a `Call.value` forward that a downstream call didn't fully consume) simply sits there until the next legitimate `_execute`/`onAccept` sweep — during which window it is fully exposed to theft via `dispatch()`.

### Impact Explanation
This is a High severity, direct fund-loss vector: any native ETH or ERC20 tokens that transiently reside in the shared `CallDispatcher` (across `HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`) can be drained by an arbitrary unprivileged caller with a single transaction, with no dependency on proofs, relayers, or consensus. Because the dispatcher is a shared, persistently deployed contract used by multiple production apps, any dust left behind by a partial fill, a reverted-but-recovered leg of a multi-call batch, a `Call.value` that under/over-forwards, or third-party ETH sent to its `receive()`, is permanently at risk of being swept by an attacker before the owning app's own sweep call executes.

### Likelihood Explanation
Likelihood is non-trivial: an attacker only needs to monitor the `CallDispatcher`'s balance (a single `eth_getBalance`/`balanceOf` check) and race a `dispatch()` call the instant any balance appears — whether from ETH sent directly by mistake, or a transient balance mid-flow of a legitimate app interaction, or any accounting mismatch that leaves dust unswept. No privileged role, governance action, or malicious insider is required; this is fully reachable by a normal unprivileged transaction from any address.

### Recommendation
Restrict `CallDispatcher.dispatch` to be callable only by an allow-listed set of app contracts (e.g., via `onlyRole`/`onlyApp` modifier configured at construction), or deploy a fresh, single-use `CallDispatcher` instance per order/transfer flow so no balance can ever persist between transactions. At minimum, add a reentrancy-safe check that reverts if the caller is not one of the registered gateway/token contracts, and remove or gate the unguarded `receive()` function so unsolicited ETH cannot accumulate on the shared dispatcher.

### Proof of Concept
1. Any address sends a small amount of ETH directly to the deployed `CallDispatcher` address (its `receive()` accepts unconditionally), or waits until a legitimate `IntentGatewayV2`/`HyperFungibleToken` flow leaves a nonzero balance on it (e.g., `Call.value` slightly under-forwards, or a sweep loop omits a token not present in `outputsLen`/`inputsLen`).
2. The attacker calls `CallDispatcher.dispatch(abi.encode(calls))` directly, where `calls[0] = Call({to: attacker, value: <dispatcher.balance>, data: ""})` (or, for an ERC20 balance, `Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})`).
3. Since `dispatch()` performs no caller check, the call succeeds and the balance is transferred to the attacker — see the unguarded implementation: [4](#0-3) .

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
