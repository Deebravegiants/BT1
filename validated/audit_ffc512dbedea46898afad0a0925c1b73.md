### Title
Missing zero-amount transfer guard in `IntentGatewayV2.withdraw()` can permanently brick escrow settlement for revert-on-zero-transfer tokens - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron `IntentGatewayV2.withdraw()` function unconditionally calls `token.call(...transfer...)` (or a native `.call{value: amount}`) for every entry in `body.tokens`, with no guard skipping zero-amount entries. This is the same bug class as the reported `Backstop.claim()` issue: a missing `if (amount > 0)` check before performing a transfer that a "revert on zero value transfer" ERC-20 will reject, causing the whole settlement transaction to revert unrecoverably.

### Finding Description
`withdraw()` is the terminal function that releases escrowed order inputs to a beneficiary for both `RedeemEscrow` (solver payout) and `RefundEscrow` (cancellation refund), and is invoked from `onAccept()` for cross-chain settlement messages and directly from `cancelOrder()` for same-chain cancellation: [1](#0-0) 

Note the loop body performs the token transfer for every entry unconditionally:
```solidity
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
    ...
```
This differs from the newer, audited implementation in `IntentsBase._withdraw()` used by the EVM mainline `IntentGatewayV2`, which explicitly guards against zero amounts before attempting a transfer: [2](#0-1) 

```solidity
for (uint256 i; i < len; i++) {
    ...
    uint256 amount = body.tokens[i].amount;
    if (amount == 0) continue;
    ...
```
The Tron contract is missing this exact guard. `withdraw()` is reached from `onAccept()` for `RedeemEscrow`/`RefundEscrow` requests delivered by any relayer: [3](#0-2) 

and from `cancelOrder()`'s same-chain path, which is directly callable by the order owner: [4](#0-3) 

If a token registered as an order input is a "revert on zero value transfer" ERC-20 and a `body.tokens[i].amount` entry of `0` reaches `withdraw()` while `_orders[commitment][token]` is still non-zero (e.g. via proportional/partial-fill rounding down to zero, or a multi-entry input list where one entry legitimately nets to zero after accounting), the `token.call(...)` will return `success == false`, and `withdraw()` reverts with `TransferFailed()`. Because this call is reached from ISMP message delivery (`onAccept`), a relayer cannot get this settlement message accepted — the request will perpetually fail to be delivered, and the escrowed principal for that commitment becomes permanently stuck (no other function unwinds `_orders[commitment]`).

### Impact Explanation
This blocks the terminal escrow-release path for `RedeemEscrow`/`RefundEscrow` messages, meaning a solver's payout or a user's refund can never be delivered for the affected order/token combination once triggered — permanently freezing the escrowed input funds and creating a route that is unable to deliver messages, matching the "permanent freezing of funds" / "route unable to deliver messages" impact classes.

### Likelihood Explanation
Likelihood depends on (a) an order using a revert-on-zero-transfer ERC-20 as an input token, and (b) a code path producing a `body.tokens[i].amount == 0` entry for a token whose escrow balance is still non-zero (so it doesn't short-circuit on `UnknownOrder()`). The predispatch/partial-fill/rounding paths in this contract are user- and solver-influenced (not privileged/governance), so this is reachable by an ordinary user placing an order or a solver structuring a partial fill, without any admin/governance action.

### Recommendation
Add the same `if (amount == 0) continue;` guard used in `IntentsBase._withdraw()` to the Tron `IntentGatewayV2.withdraw()` loop before performing the native/ERC-20 transfer, so zero-amount entries are skipped rather than attempted.

### Proof of Concept
Not independently reproduced with a full test run; conceptual PoC based on code reading:
1. Deploy `IntentGatewayV2` (Tron variant) with a token `T` that reverts on `transfer(to, 0)`.
2. Construct an order whose `inputs` include an entry for `T` such that, through the predispatch flow or multi-entry accounting, the value delivered in a subsequent `WithdrawalRequest.tokens` entry for `T` is `0` while `_orders[commitment][T]` remains non-zero.
3. Trigger settlement via `onAccept()` (RedeemEscrow/RefundEscrow) or `cancelOrder()` same-chain path — `withdraw()` calls `T.call(transfer(beneficiary, 0))`, which reverts, causing `TransferFailed()` and the escrow settlement to permanently fail. [5](#0-4)

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L456-470)
```text
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```
