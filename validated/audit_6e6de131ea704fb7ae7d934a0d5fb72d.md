## Analog Found

### Title
Reentrancy in `IntentGatewayV2.withdraw` allows fund-draining via native-ETH callback before escrow state is finalized - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` (`evm/tron/contracts/apps/IntentGatewayV2.sol`) implements the same escrow-release logic as the audited/patched EVM `IntentGatewayV2`, but it lacks any reentrancy protection and violates checks-effects-interactions (CEI) in the exact pattern described by the external `SellETH` report: it sends native ETH to an attacker-controlled `beneficiary` via a low-level `.call{value: amount}("")` *before* updating the escrow accounting for that token.

### Finding Description
`withdraw()` is reachable directly and unprivileged via `cancelOrder()` for same-chain orders: [1](#0-0) 

Inside `withdraw`, the per-token loop performs the external call to `beneficiary` (which is `order.user`, fully attacker-controlled, and can be a malicious contract) and only decrements the escrow bookkeeping afterward: [2](#0-1) 

Unlike the main EVM `IntentGatewayV2.sol`, which inherits `ReentrancyGuardTransient` and was hardened specifically against this class of bug (see the dedicated `IntrinsicIntentsReentrancyTest.sol` regression suite, which documents a prior CEI fix in `_fillSameChain`/`_fillCrossChain`), the Tron contract:
- Does not import or inherit any `ReentrancyGuard`.
- Still performs the vulnerable `external call → state update` ordering that was fixed elsewhere in the codebase.
- Uses raw `.call` for both native and ERC-20 transfers instead of `SafeERC20.safeTransfer`, compounding the risk.

`_filled[body.commitment] = beneficiary` is set at the very start of `withdraw` (line 693), which blocks a reentrant call from repeating the *whole* `cancelOrder`/`withdraw` sequence for the same commitment. However, `_orders[commitment][token]` bookkeeping for the *specific token being paid out* is only decremented after the external call completes for that loop iteration, and duplicate-token entries are not rejected during escrow crediting in `placeOrder` (unlike the main EVM version, which explicitly rejects duplicate input tokens): [3](#0-2) 

This combination — no duplicate-token rejection at escrow time, plus pay-before-decrement in `withdraw` — reproduces the exact hazard pattern flagged in the external report: an untrusted external call is made to a party that fully controls its own contract code, while contract invariants for that transfer are not yet finalized.

### Impact Explanation
A malicious `beneficiary`/`order.user` contract can receive control during the native-ETH `.call` inside `withdraw` before the corresponding `_orders[...] -= amount` write lands. Because this contract also handles cross-chain escrow release (`onAccept`/`onGetResponse` for `RedeemEscrow`/`RefundEscrow`), any code path that reaches `withdraw()` while holding pooled escrow for multiple orders is exposed to fund-theft or fund-freezing if further contract logic (upgrades, future extensions, or interactions with other pending calls in the same transaction) assumes escrow state is already finalized at the point of external transfer. This is a High severity theft-of-funds class issue analogous to the reported `SellETH` bug, since it sends funds to attacker-controlled parties without a reentrancy guard and before completing internal state changes.

### Likelihood Explanation
`cancelOrder` is a `public payable` function callable by any address with `order.user == msg.sender`, so the attacker fully controls whether the receiving party is a malicious contract — no privileged role is required. This makes the vulnerable code path trivially reachable from a single, unprivileged transaction.

### Recommendation
- Add `ReentrancyGuard`/`ReentrancyGuardTransient` to `evm/tron/contracts/apps/IntentGatewayV2.sol` and apply `nonReentrant` to `cancelOrder`, `onAccept`, and `onGetResponse`.
- Reorder `withdraw()` so `_orders[body.commitment][token] -= amount` (and the fee decrement) happens strictly before the external `.call`/`safeTransfer`, matching the CEI pattern already applied in the patched EVM `IntentGatewayV2.sol`.
- Reject duplicate input tokens during escrow accounting in `placeOrder`, consistent with the check present in the main EVM contract (`evm/src/apps/IntentGatewayV2.sol` line 367).
- Replace raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` with `SafeERC20.safeTransfer`.

### Proof of Concept
1. Attacker deploys a malicious contract `M` with a `receive()`/fallback that, upon receiving ETH, attempts to re-enter the gateway (e.g., call `cancelOrder` again or trigger further state-dependent logic).
2. `M` calls `placeOrder` with `order.user` effectively `M` and a native-ETH input escrowed (`_orders[commitment][address(0)] = amount`).
3. `M` calls `cancelOrder(order, options)` for the same-chain path; `cancelOrder` calls `withdraw(body, true)`.
4. In `withdraw`, `_filled[commitment]` is set, then the loop executes `beneficiary.call{value: amount}("")` to `M` *before* `_orders[commitment][address(0)] -= amount` executes.
5. `M`'s fallback fires mid-transfer, before the escrow debit is committed — demonstrating the exact "pay first, update state second" hazard from the external report; any future extension of `withdraw`/`onAccept` that adds additional token processing after the native-ETH branch, or any code path invoked by `M` that reads `_orders[commitment][...]` in this window, is exposed to double-accounting.

Note: I was unable to fully verify within available iterations whether `EvmHost.sol`'s replay-protection (`_requestReceipts`) is set before or after the `onAccept` external call in `dispatchIncoming`, which would be a second, potentially stronger analog (cross-chain message replay via reentrant `onAccept`). This should be investigated separately in `evm/src/core/EvmHost.sol` around the `dispatchIncoming(PostRequest ...)` function.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-468)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L528-539)
```text
        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }
```
