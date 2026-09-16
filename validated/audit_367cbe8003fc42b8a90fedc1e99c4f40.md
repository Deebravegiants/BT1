## Title
Unchecked low-level ERC20 `transfer` calls in `IntentGatewayV2.withdraw` / `onAccept` (SweepDust) can silently fail and permanently freeze escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The external-report bug class ("transfer function is not protected... no checks for a successful transfer of tokens") maps directly onto the Tron fork of `IntentGatewayV2`. Its `withdraw()` function — reachable by any user via `placeOrder()` + `cancelOrder()` — releases escrowed ERC20 tokens using a raw low-level `.call()` with the `IERC20.transfer` selector and only checks that the call itself did not revert, not that the token actually returned `true`. The same pattern is used for the `SweepDust` action inside `onAccept`. This is a direct regression versus the hardened main-chain implementation, which correctly uses OpenZeppelin's `SafeERC20.safeTransfer`.

### Finding Description
`withdraw()` iterates over the order's escrowed tokens and, for ERC20s, performs: [1](#0-0) 

```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;
```

`success` here only reflects whether the external call reverted — not whether the token's `transfer()` function actually returned `true`. Standard ERC20 tokens that return `false` on failure (instead of reverting) will make this branch treat the transfer as successful. Immediately afterward, `_orders[body.commitment][token]` is unconditionally decremented (and, for the fee branch, `delete`d), permanently marking the escrow as redeemed even though no tokens moved.

The identical unchecked pattern also appears in the `SweepDust` handler inside `onAccept`: [2](#0-1) 

This function is reachable from ordinary user flows:
- `placeOrder()` escrows arbitrary attacker-chosen tokens under a fresh commitment.
- `cancelOrder()` (same-chain path) is directly callable by the order owner and calls `withdraw()` synchronously. [3](#0-2) 

Once `withdraw()` runs, `_filled[commitment]` is set and `_orders[...]` is zeroed regardless of whether the transfer genuinely succeeded, so the funds become permanently unrecoverable — there is no other code path that re-attempts delivery for that commitment.

By contrast, the main EVM implementation of the same logic (`IntentsBase._withdraw`) correctly uses `SafeERC20.safeTransfer`, which reverts on a `false` return, and also fixes the ordering (state updated before external call): [4](#0-3) 

The Tron variant does neither — it neither checks the boolean return of `transfer()` nor updates state before the external call, showing that this is an un-hardened, older copy of the escrow-release logic. This mirrors the original Cooler.sol report's very complaint: "no checks for a successful transfer of tokens" plus interactions-before-effects ordering.

### Impact Explanation
Any user's escrowed principal, transaction fees, or dust that is denominated in a non-reverting ERC20 (which reverts-vs-returns-false semantics are common in real-world tokens, and can also be trivially crafted by an attacker who controls the input token in same-chain `cancelOrder`) can be permanently locked in the contract: `_orders` accounting is zeroed and `_filled` is set, so the beneficiary can never re-claim, yet the tokens were never actually moved out of the gateway. This is a permanent freezing of user or protocol funds, satisfying the High-severity bar (concrete, permanent loss of funds), reachable from a single `cancelOrder` transaction with no privileged access required.

### Likelihood Explanation
High likelihood: the vulnerable code path is exercised on every `RedeemEscrow`/`RefundEscrow`/`SweepDust`/same-chain-cancel flow that involves ERC20 tokens, requiring only a normal user transaction (`placeOrder` + `cancelOrder`) or a routine cross-chain settlement dispatched by a relayer. No governance or privileged role is needed to trigger it, and an attacker can guarantee the failure mode by escrowing a token they control whose `transfer()` returns `false` under attacker-chosen conditions.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and in the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer`, matching the already-fixed main EVM `IntentsBase._withdraw` implementation. Additionally, decrement/delete `_orders[...]` (effects) before performing the external transfer (interactions) to fully align with checks-effects-interactions, consistent with the pattern already adopted in `evm/src/apps/intentsv2/IntentsBase.sol`.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC20 whose `transfer()` returns `false` (without reverting) whenever called by the `IntentGatewayV2` contract (or under an attacker-chosen condition).
2. Attacker calls `placeOrder()` with `order.inputs = [{token: EvilToken, amount: X}]`, escrowing `X` EvilTokens; `_orders[commitment][EvilToken] += X`.
3. Attacker calls `cancelOrder(order, options)` on the same chain before any fill. This synchronously invokes `withdraw(body, true)`:
   - `_filled[commitment]` is set.
   - `token.call(transfer(...))` succeeds at the call level (`success = true`) but the token silently returns `false`, so no tokens are actually transferred to the beneficiary.
   - `_orders[commitment][EvilToken] -= X` zeroes the escrow record.
4. The transaction completes without reverting; `EscrowRefunded` is emitted, but the `EvilToken` balance still sits in `IntentGatewayV2` and can never be reclaimed by the attacker or anyone else, since `_orders` and `_filled` now report the order as fully settled — resulting in permanently frozen tokens.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-539)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-676)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
