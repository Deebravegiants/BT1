### Title
Reflection/rebasing-token balance inflation exploited via `IntentGatewayV2`'s shared `CallDispatcher` predispatch sweep - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`placeOrder`'s predispatch path sweeps *whatever balance* the shared `CallDispatcher` holds of a token and credits the entire swept amount as escrow for the order that triggered the sweep, exactly the "trust the live `balanceOf()` reading instead of the actual value transferred" pattern that let the FDP attacker inflate a pair's tracked balance with `deliver()` and drain real WBNB from it.

### Finding Description
In `placeOrder` the fee-on-transfer accommodation logic does not merely measure "amount transferred in this call" — it sweeps the dispatcher's *entire* current balance of each input token and attributes it to the current order: [1](#0-0) 

```solidity
uint256 balance = IERC20(token).balanceOf(dispatcher);
...
transferCalls[i] = Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)});
...
received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
if (received > order.inputs[i].amount) { emit DustCollected(...); }
else { order.inputs[i].amount = received; }
```

`_params.dispatcher` is a single shared `CallDispatcher` instance used by every order/user of this gateway deployment — it is not created per-order: [2](#0-1) 

For a rebasing/reflective ERC-20 (like `FDP` in the referenced report, whose `deliver()` burns the caller's own raw balance while inflating the reflection rate that every *other* holder's `balanceOf()` is computed from), an attacker does not need to transfer a single wei into the dispatcher to inflate its `balanceOf()` reading. If the dispatcher already carries *any* nonzero balance of such a token (which is expected by design — dust is explicitly retained rather than swept back to zero, and multiple concurrent `placeOrder` calls into the same shared dispatcher are the documented normal flow for fee-on-transfer tokens), the attacker can, from an entirely separate address holding a large stash of the same token, call the token's `deliver()`-style function. This burns the attacker's own balance and proportionally *increases* the tracked `balanceOf()` of every other holder of the token, including the dispatcher, without any `transfer()` event or actual movement of funds into the dispatcher.

The next `placeOrder` call that routes that same token through the predispatch/sweep path reads `IERC20(token).balanceOf(dispatcher)`, sees the inflated figure, and credits `order.inputs[i].amount` (i.e., real escrow entitlement, later paid out to whichever solver fills the order) to that inflated figure — value that was never actually transferred to the gateway. This is the same mechanic as `FDP_WBNB.swap()` reading an artificially inflated `FDP` balance on the pair after the attacker's `deliver()` call and paying out real WBNB against it.

### Impact Explanation
Escrow accounting in `IntentGatewayV2` is meant to be strictly backed by tokens actually held by the contract (this is explicitly why the fee-on-transfer "measure actual received" logic exists at all — see the fee-on-transfer regression tests). The predispatch sweep path breaks that invariant for reflective/rebasing tokens by trusting a live `balanceOf()` snapshot of a *shared* pooled account instead of a per-call transfer delta, allowing an attacker to manufacture escrow entitlement (and thus solver payout / withdrawal) that is not backed by tokens they deposited — a concrete unbacked-value/theft class of bug reachable from a single `placeOrder` transaction.

### Likelihood Explanation
Exploitability is conditioned on: (1) the gateway allowing the attacker to select an arbitrary reflective/rebasing ERC-20 as an input token with a `predispatch` leg (no on-chain allowlist of input tokens was found in the reviewed code), and (2) the shared `CallDispatcher` already holding, or being made to hold via the attacker's own predispatch deposit plus subsequent `deliver()` calls, a nonzero balance of that token. Since the sweep path is explicitly designed to sweep "whatever is on the dispatcher," and dispatcher balance persists across unrelated orders/users by design, an attacker fully controls both preconditions using only their own funds and a single `placeOrder` transaction, making this readily reachable without any privileged role.

### Recommendation
Do not trust a live `balanceOf(dispatcher)` snapshot as the escrowed amount. Track exactly what was transferred to the dispatcher during *this* call (e.g., cap the swept amount to `predispatch` deposit amount plus any calldata-returned proceeds accounted for explicitly, or require the dispatcher to be a fresh, single-use contract/clone per order so no balance can accumulate or be manipulated by third parties between calls). At minimum, reject input tokens whose `balanceOf` semantics are not a simple additive ledger (deny known-rebasing tokens), or bound the swept "received" amount to the actual token `transfer` events emitted by the predispatch call rather than a coarse before/after balance diff on a shared account.

### Proof of Concept
Not independently reproducible from the indexed code alone — the exploit requires deploying a concrete reflective-ERC20 (mirroring `FDP`'s `deliver()` mechanic) and driving it through `IntentGatewayV2.placeOrder`'s predispatch/sweep branch. This is consistent with the referenced `DeFiHackLabs` PoC's structure (flash-loan swap into the reflective token, call `deliver()` to inflate a third party's tracked balance, then extract real value against the inflated reading) but adapted to `evm/src/apps/IntentGatewayV2.sol` lines 260–311 instead of a Uniswap V2 pair swap. I was not able to fully verify whether an input-token allowlist exists elsewhere in governance-set parameters (`_params`) that would block arbitrary/malicious ERC-20s from being used as `order.inputs`/`predispatch.assets` tokens — this should be confirmed in a live session, as its absence is required for the finding to be exploitable.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L260-311)
```text
            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

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

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/utils/CallDispatcher.sol (L25-63)
```text
contract CallDispatcher is ICallDispatcher {
    /**
     * @dev error thrown when the target is not a contract.
     */
    error NotContract(address target);

    /**
     * @dev error thrown when a call fails.
     */
    error CallFailed(address target, bytes result);

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
}
```
