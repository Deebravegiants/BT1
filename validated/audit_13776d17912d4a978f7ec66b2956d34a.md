### Title
Missing zero-address validation for `Order.output.beneficiary` in `placeOrder` permanently locks solver output funds - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder` accepts an arbitrary `Order.output.beneficiary` (a `bytes32`-encoded address) with no validation that it is non-zero. This value is later used, unchanged, as the destination for the solver's output payment when the order is filled and eventually withdrawn via `_withdraw`/`withdraw` in `IntentsBase.sol` / `IntentGatewayV2.sol` (tron variant). If a user submits (or the order is otherwise generated with) a zero-address beneficiary, the solver's tokens sent to satisfy the order are burned to `address(0)` with no way to recover them, mirroring the reported `SolverVaults.requestWithdraw` receiver bug.

### Finding Description
`placeOrder` stamps `order.user`, `order.source`, and `order.nonce`, but never touches or validates `order.output.beneficiary`: [1](#0-0) 

The commitment is computed over the full order (including `output.beneficiary`), and it is emitted verbatim in `OrderPlaced`: [2](#0-1) 

When a solver fills the order and it is finally settled, `beneficiary` is decoded straight from the (attacker/user-controlled) order/withdrawal request and used as the transfer target with no zero-address check, for both native and ERC20 assets: [3](#0-2) 

The Tron variant of the same contract shows the identical unguarded pattern, including a raw low-level `.call{value: amount}` transfer to `beneficiary`, which will succeed silently even when `beneficiary == address(0)`: [4](#0-3) 

Because Solidity `address(uint160(uint256(bytes32(0))))` evaluates to `address(0)`, and a plain `call{value: amount}("")` to `address(0)` succeeds (ETH is simply burned) and an ERC20 `transfer`/`safeTransfer` to `address(0)` is the only path that would revert (most standard ERC20s reject transfers to the zero address, but the raw `.call` path in the Tron/low-level variant does not check the return data for that specific case and could still "succeed" per its own bespoke handling) — a beneficiary of the zero address results in permanent loss of the solver's output funds for that order, exactly analogous to the reported `SolverVaults` bug where a zero-address `receiver` locks collateral forever.

### Impact Explanation
This is reachable by any unprivileged user submitting a single `placeOrder` transaction with `output.beneficiary == bytes32(0)` (or a beneficiary field derived from unchecked off-chain/coprocessor input, e.g. a malformed phantom order or user_op). Any solver who unknowingly fills such an order (native-asset outputs, or non-standard token outputs that don't hard-revert on transfer-to-zero) has its output payment burned irrecoverably — a direct, permanent loss of solver funds with no compensating escrow release, matching the "permanent freezing/loss of funds" acceptance criteria.

### Likelihood Explanation
Medium likelihood: this requires either (a) a mistake/misconfiguration by the order-placing user or off-chain tooling (as in the original Sherlock finding, this is typically an honest-mistake bug class rather than an intentional attack, but it could also be griefed deliberately by a malicious order placer targeting a specific solver for a native-asset trade), or (b) a solver filling an order without independently sanity-checking `output.beneficiary != 0` before committing funds. Since `placeOrder` performs no server-side validation, nothing prevents such an order from being placed and advertised for fills.

### Recommendation
Add an explicit check in `placeOrder` (in both `evm/src/apps/IntentGatewayV2.sol` and the Tron variant `evm/tron/contracts/apps/IntentGatewayV2.sol`) that reverts with `InvalidInput()` (or a new dedicated error) when `order.output.beneficiary == bytes32(0)`. As defense in depth, also validate `beneficiary != address(0)` inside `_withdraw`/`withdraw` in `IntentsBase.sol` before executing native or ERC20 transfers.

### Proof of Concept
1. User calls `placeOrder(order, graffiti)` with `order.output.beneficiary = bytes32(0)` and a native-token output asset. No revert occurs — `placeOrder` has no check on `beneficiary` [1](#0-0) .
2. A solver calls `fillOrder(order, options)`, routes through `_fillSameChain`/`_fillCrossChain`, which eventually calls `_withdraw`, decoding `beneficiary = address(uint160(uint256(order.output.beneficiary))) == address(0)` [3](#0-2) .
3. For a native-token output, `_sendValue(address(0), amount)` (or the equivalent raw `.call{value: amount}("")` in the Tron variant) succeeds and the solver's ETH is burned to the zero address with no recovery mechanism [5](#0-4) .

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-227)
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

**File:** evm/src/apps/IntentGatewayV2.sol (L399-414)
```text
        emit OrderPlaced({
            user: order.user,
            source: string(order.source),
            destination: string(order.destination),
            deadline: order.deadline,
            nonce: order.nonce,
            fees: order.fees,
            session: order.session,
            predispatch: order.predispatch.assets,
            inputs: reducedInputs,
            beneficiary: order.output.beneficiary,
            outputs: order.output.assets,
            predispatchCall: order.predispatch.call,
            outputCall: order.output.call,
            graffiti: graffiti
        });
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
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
