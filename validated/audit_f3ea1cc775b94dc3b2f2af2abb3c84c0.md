Confirmed: `IntentGatewayV2` (Tron variant) contract inherits only `HyperApp, EIP712` — **no `ReentrancyGuard`, no `nonReentrant` modifier anywhere in the file**, and `cancelOrder`/`placeOrder`/`fillOrder` are plain `public payable` functions [1](#0-0) . This, combined with the pre-storage-update external token call in `withdraw()`, gives a concrete, unprivileged reentrancy path into the shared escrow pool.

### Title
Reentrant escrow drain via pre-effects external token transfer in Tron `IntentGatewayV2.withdraw` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron build of the Intent Gateway's `withdraw()` function sends tokens to the beneficiary via a raw low-level `.call` **before** decrementing the `_orders[commitment][token]` escrow accounting, and neither `withdraw()` nor its only unprivileged caller, the same-chain branch of `cancelOrder()`, is protected by a reentrancy guard. This lets an attacker who places an order using a malicious ERC20/TRC20 as an input token reenter the gateway during the token transfer callback and repeatedly withdraw against the same (not-yet-decremented) escrow balance, draining real token balance that belongs to the shared pool of all other orders/positions held by the contract — directly analogous to mySwap CL's incident where a large shared pool of residual positions was drained through a single exploitable code path.

### Finding Description
`withdraw()` in the Tron gateway:
```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    _filled[body.commitment] = beneficiary;

    uint256 len = body.tokens.length;
    for (uint256 i; i < len;) {
        address token = address(uint160(uint256(body.tokens[i].token)));
        uint256 amount = body.tokens[i].amount;
        if (_orders[body.commitment][token] == 0) revert UnknownOrder();

        if (token == address(0)) {
            (bool sent,) = beneficiary.call{value: amount}("");
            ...
        } else {
            (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
            ...
        }

        _orders[body.commitment][token] -= amount;   // <-- effect happens AFTER interaction
        unchecked { ++i; }
    }
    ...
}
``` [2](#0-1) 

This is a checks-effects-interactions violation: the external `token.call(...)` (interaction) executes while the escrow ledger (`_orders[...]`) still reflects the pre-withdrawal balance (effect not yet applied). Compare this with the audited mainline EVM contract, `IntentsBase._withdraw`, which decrements `_orders[body.commitment][token]` *before* calling `safeTransfer`/`_sendValue` [3](#0-2)  — the Tron variant has regressed this ordering.

The only unprivileged, single-transaction path into `withdraw()` is the same-chain branch of `cancelOrder()`, callable directly by `order.user`:
```solidity
function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
    ...
    if (isSameChain) {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        if (orderSource != currentChain) revert WrongChain();
        WithdrawalRequest memory body = WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});
        withdraw(body, true);
    }
    ...
}
``` [4](#0-3) 

Neither `cancelOrder` nor `withdraw` carries a `nonReentrant` modifier, and the contract does not inherit `ReentrancyGuard` at all [1](#0-0)  — unlike the mainline `IntentGatewayV2.cancelOrder`, which is `nonReentrant` [5](#0-4) .

Because `order.inputs[i].token` is attacker-controlled at `placeOrder` time (any TRC20/ERC20 address can be used as the escrowed input token, and the gateway invokes `.call(...)` on it rather than a trusted, hard-coded token), the attacker can deploy a token contract whose `transfer()` callback reenters `cancelOrder()` for the same order/commitment. On each reentrant call, `_orders[body.commitment][token]` is still non-zero (decrement happens only after the call returns), so `UnknownOrder()` does not trip, and another `amount` is sent out. Recursion continues until gas is exhausted or the shared token balance held by the contract (which backs the escrow of every other user's currently-open order in that token) is emptied — the funds drained are not limited to the attacker's own escrowed deposit.

### Impact Explanation
This is a direct, unprivileged theft-of-funds path: a single user-submitted transaction (`placeOrder` with a malicious token, then `cancelOrder`) can drain the shared token balance of the `IntentGatewayV2` contract, taking funds belonging to unrelated orders/users — the same "shared pool, residual positions drained" pattern described in the mySwap CL report. This meets the "concrete theft of funds via an unauthorized app action" bar for a Medium/High-severity analog.

### Likelihood Explanation
Likelihood is high on any deployment of this Tron variant that allows a permissionless choice of input token (no token allow-list is visible in `placeOrder`) [6](#0-5) : it requires only deploying an ordinary malicious TRC20 and placing then cancelling one order — no special privileges, governance, or off-chain component involved.

### Recommendation
- Apply checks-effects-interactions in `withdraw()`: decrement `_orders[body.commitment][token]` before performing the native/token transfer, exactly as done in the mainline `IntentsBase._withdraw`.
- Add a `ReentrancyGuard` (`nonReentrant`) to `cancelOrder`, `placeOrder`, `fillOrder`, and any other externally reachable entry point that can trigger `withdraw`/token transfers, matching the mainline EVM `IntentGatewayV2`.
- Switch raw `.call` token transfers to `SafeERC20.safeTransfer`, and validate the check `_orders[commitment][token] == 0` should instead verify `amount <= escrowed` before transferring.

### Proof of Concept
1. Attacker deploys `EvilToken`, a TRC20/ERC20 whose `transfer(to, amount)` implementation, when called by the gateway, re-enters `IntentGatewayV2.cancelOrder(order, options)` with the same `order`/commitment before returning.
2. Attacker calls `placeOrder` with `order.inputs = [{token: EvilToken, amount: X}]`, `source == destination` (same-chain order), crediting `_orders[commitment][EvilToken] = X`.
3. Attacker calls `cancelOrder(order, options)` as `order.user`. This enters `withdraw(body, true)`, which reads `_orders[commitment][EvilToken] == X` (non-zero), calls `EvilToken.transfer(attacker, X)`.
4. Inside `EvilToken.transfer`, the token reenters `cancelOrder(order, options)` again. Since `_orders[commitment][EvilToken]` has not yet been decremented (the decrement happens only after the outer `.call` returns), the check `_orders[...] == 0` still passes, and another `X` tokens are sent to the attacker.
5. Step 4 repeats recursively (bounded by gas), each iteration transferring `X` more `EvilToken` tokens out of the gateway's shared balance, exceeding the attacker's own escrowed deposit and consuming balance backing other users' open orders in that token.
6. When the call stack unwinds, `_orders[commitment][EvilToken] -= X` executes once per stack frame; because the checks never re-validated against a correctly-updated balance during the reentrant calls, the attacker has already extracted more tokens than were ever legitimately escrowed for this commitment.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-469)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
        }

        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
        } else {
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
        }
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-470)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L505-505)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
```
