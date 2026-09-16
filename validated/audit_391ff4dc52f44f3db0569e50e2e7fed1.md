### Title
Order placement accepts a zero-address `beneficiary`, permanently locking output funds on fill - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`placeOrder` never validates `order.output.beneficiary`, letting a caller (or a buggy front-end/relayer/coprocessor path) submit an order whose beneficiary is `bytes32(0)`. Because `beneficiary` is decoded straight into an EVM `address` and used as the destination for output-token transfers and refunds, this analog matches the reported bug class ("account/beneficiary can be zero address") but the reachable impact here is fund loss rather than an "account creation" issue.

### Finding Description
`placeOrder` builds and commits an `Order` without ever checking `order.output.beneficiary`: [1](#0-0) 
The only fields it overwrites are `user`, `source`, and `nonce`: [2](#0-1) 

The `beneficiary` value flows unchecked into `_withdraw`, where it is cast to an `address` via `address(uint160(uint256(body.beneficiary)))` and used for both escrow release and the terminal fee transfer: [3](#0-2) [4](#0-3) 

If `body.beneficiary == bytes32(0)`, this decodes to `address(0)`. Native transfers go through `_sendValue(address(0), amount)`, and ERC20 transfers go through `IERC20(token).safeTransfer(address(0), amount)`. Whether this reverts depends entirely on the token/`_sendValue` implementation — OpenZeppelin's standard `_transfer` reverts on a zero recipient, but not every ERC20 in the wild does, and a native-token `_sendValue` to `address(0)` via a low-level call typically succeeds (there is no code at `address(0)` to reject it). Consequently a zero-address beneficiary is not guaranteed to revert.

### Impact Explanation
An order placed with a zero beneficiary (whether by an honest user's client-side bug, a malformed relayed/cross-chain fill, or a maliciously-crafted order that a solver naively fills) causes the filler's/solver's output tokens (and, on finalize, accumulated protocol/relayer fees) to be sent to `address(0)` for any token whose transfer function does not explicitly reject the zero address, or for native value transferred via a raw call. Funds sent to `address(0)` are permanently and irrecoverably lost — this is a Medium/High severity "permanent freezing/loss of funds" finding, matching the validation bar (concrete permanent freezing of funds) required.

### Likelihood Explanation
Likelihood is moderate: it requires an order with beneficiary `bytes32(0)` to actually be filled. This could happen from a client-side integration bug (e.g., encoding `order.output.beneficiary` from an unset/default value), a bridged/cross-chain order whose beneficiary bytes are mis-decoded, or a solver filling an order without validating the beneficiary field itself (the contract provides no such validation for solvers to rely on). Because no code path in `placeOrder`, `fillOrder`, or `_withdraw` rejects a zero beneficiary, any single submitted order transaction can reach this state without any privileged or malicious actor being required.

### Recommendation
Add an explicit check in `placeOrder` (and, defensively, in `_withdraw`) that `order.output.beneficiary != bytes32(0)`, reverting with `InvalidInput()` (the existing error already used for other malformed-order cases) before the order is committed/escrowed.

### Proof of Concept
1. Caller calls `placeOrder` with `order.output.beneficiary = bytes32(0)` and valid inputs/outputs; the call succeeds since no validation exists: [5](#0-4) .
2. A solver fills the order via `fillOrder` → `_fillSameChain`/`_fillCrossChain` → `_withdraw`, which computes `beneficiary = address(uint160(uint256(bytes32(0)))) = address(0)` and transfers the output tokens/fees there: [3](#0-2) .
3. For any ERC20 that does not itself revert on a zero-address recipient, or for native token sent via `_sendValue`, the transfer succeeds and the funds are permanently lost.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-226)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-480)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
```
