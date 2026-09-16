Found a concrete, unprivileged-reachable analog: the Tron variant of `IntentGatewayV2.sol` violates checks-effects-interactions in the same way as the reported `Bond.sol` bug, and it is directly reachable via `cancelOrder()`, which is a `public` function callable by any order owner — no `onlyOwner`/`onlyHost` gate on the entry point that triggers the vulnerable code path in the same-chain case.

### Title
Reentrancy in `IntentGatewayV2.withdraw()` (Tron) via same-chain `cancelOrder()` — external transfer precedes escrow-balance decrement - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron port of `IntentGatewayV2` performs the low-level token/native transfer to the beneficiary *before* decrementing the corresponding escrow balance in `_orders[commitment][token]`, and *before* clearing the accumulated fee entry. This is the same checks-effects-interactions violation described in the `Bond.sol` `withdrawExcessCollateral`/`withdrawExcessPayment` finding, and unlike the mainline EVM `IntentsBase.sol`/`ExtrinsicIntents.sol` implementation (which was already hardened to update `_orders` before transferring, per the referenced fix), this Tron contract still transfers-then-decrements.

### Finding Description
`withdraw()` in [1](#0-0)  loops over `body.tokens`, and for each token:
1. checks `_orders[commitment][token] == 0`
2. sends the tokens/ETH via a raw `.call` to `beneficiary` or `token.call(transfer(...))`
3. only *afterwards* does `_orders[commitment][token] -= amount`

The same pattern repeats for the accumulated transaction fee: the fee token is transferred out via `.call`, and only afterward is `_orders[commitment][TRANSACTION_FEES]` deleted, at [2](#0-1) .

`withdraw()` is invoked from the same-chain branch of `cancelOrder(order, options)`, a `public` function with no reentrancy guard anywhere in the file (no `ReentrancyGuard`/`nonReentrant` import or modifier exists in this contract). In the same-chain path, any order owner can trigger it directly and unconditionally: [3](#0-2) 

Because `beneficiary` is `order.user` (attacker-controlled — the caller set `order.user = msg.sender` at `placeOrder` time, see [4](#0-3) ) and can be a contract, and because `token` can also be an attacker-supplied ERC20-like address for multi-token orders, the beneficiary/token contract's callback (native ETH `receive()`/fallback, or a malicious ERC20's `transfer` hook) fires *before* `_orders[commitment][token]` is decremented. From that callback the attacker can re-enter `cancelOrder()` for the very same order/commitment (the only guard, `_filled[commitment] != address(0)`, is never set on the same-chain cancel path in `withdraw()` — unlike `ExtrinsicIntents._withdraw`, this `withdraw()` never sets `_filled[commitment]`), and `_orders[commitment][token]` is still non-zero, passing the `== 0` check again and draining the same escrow entry a second (or Nth) time before the first call's decrement executes.

### Impact Explanation
This allows theft of escrowed order funds: a malicious order owner can drain more collateral/payment tokens than were ever escrowed for their order, directly stealing protocol/solver funds held by the Tron `IntentGatewayV2` contract — a concrete, unbacked-withdrawal / theft-of-funds impact matching the required severity bar (Medium/High per the report's classification of the identical bug pattern).

### Likelihood Explanation
High likelihood given reachability: `cancelOrder()` is a fully public, unprivileged entry point invokable by any order placer with a single transaction and no proof/relayer dependency for the same-chain path, and the attacker fully controls both `order.user` (the beneficiary) and can escrow a token of their choosing (an ERC20 with a transfer hook, or use the native-ETH branch with a malicious `receive()`), making the reentrancy trivially triggerable without any privileged role, unlike the original `Bond.sol` report which required a malicious `onlyOwner`.

### Recommendation
Apply the checks-effects-interactions pattern used in the mainline `IntentsBase.sol`/`ExtrinsicIntents.sol` fix: decrement `_orders[commitment][token]` (and delete the `TRANSACTION_FEES` entry, and set `_filled[commitment]`) *before* performing any external call/transfer in `withdraw()`. Additionally, add a `nonReentrant` guard to `cancelOrder()` (and any other public entry point that can reach `withdraw()`), matching the recommendation from the referenced audit finding.

### Proof of Concept
1. Attacker calls `placeOrder()` with `order.inputs` = `[{token: maliciousERC20 or address(0), amount: X}]`, which sets `order.user = attacker` and escrows `X` into `_orders[commitment][token]`.
2. Attacker (as `order.user`) calls `cancelOrder(order, options)` on the same chain (`orderSource == orderDest`), which reaches the same-chain branch and calls internal `withdraw(body, true)` at [5](#0-4) .
3. Inside `withdraw()`, the loop at [6](#0-5)  checks `_orders[commitment][token] != 0`, then calls `beneficiary.call{value: amount}("")` (or `token.call(transfer(...))`). If `beneficiary`/`token` is an attacker-controlled contract, its callback re-enters `cancelOrder(order, options)` for the identical `order`/`commitment` before `_orders[commitment][token] -= amount` executes.
4. Since `_filled[commitment]` is never set by this `withdraw()` path and `_orders[commitment][token]` is still non-zero, the reentrant call passes the same checks and transfers the escrowed amount again, repeating up to the limits of gas/recursion depth — draining more than the single `X` amount originally escrowed.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-346)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```
