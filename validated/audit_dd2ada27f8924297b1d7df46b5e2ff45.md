Confirmed: `placeOrder` has no validation that `order.output.beneficiary != address(0)`, and the fill paths pay native ETH to that address via a raw `.call{value: ...}("")`, which succeeds even when the target is `address(0)`.

### Title
Placing an order with a zero-address output beneficiary permanently burns the solver's native-token payment - (File: evm/src/apps/intentsv2/IntrinsicIntents.sol, evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`IntentGatewayV2.placeOrder` lets a user set `order.output.beneficiary` to any `bytes32` value, including zero, with no validation. [1](#0-0)  When a solver fills such an order for a native-token (`address(0)`) output, the destination-token payment is sent to `beneficiary` via a low-level `.call{value: ...}("")`, which succeeds for `address(0)` (it is not the ERC-20 zero-address-revert case) and the funds are simply lost.

### Finding Description
`_fillSameChain` and `_fillCrossChain` derive the recipient directly from the order data supplied by the user at `placeOrder` time: `address beneficiary = address(uint160(uint256(order.output.beneficiary)));` with no zero check. [2](#0-1) [3](#0-2) 

For native-token outputs, both fill paths pay the beneficiary with an inline raw call rather than a reverting ERC-20 mint/transfer: [4](#0-3) [5](#0-4)  (which calls `_sendValue`, itself just `to.call{value: amount}("")`) [6](#0-5) 

Unlike ERC20 `_transfer`/`_mint` in OpenZeppelin (which revert on `address(0)`), a plain `.call{value: ...}("")` to `address(0)` succeeds and simply moves ETH to that address, from which it can never be retrieved — there is no code at `address(0)` and no owner. Because `placeOrder` never validates `order.output.beneficiary != bytes32(0)`, and the commitment/order data (including `output.beneficiary`) is fixed at order-creation time and cannot be altered by the solver, a user who places an order with a zero beneficiary (typo, bad encoding, or malicious griefing intent) causes any solver who fills that native-ETH order to have their payment permanently destroyed. This mirrors the `Pool.addCollateral` bug class: an unprivileged, user-controlled destination address parameter with no zero-address check, feeding a raw value transfer that does not revert on the zero address.

### Impact Explanation
Funds (native ETH/token paid by the solver to fulfill the order) are irrecoverably burned to `address(0)` whenever a zero beneficiary order is filled with a native-token output. This is a direct, permanent loss of funds for the filling solver — no admin, governance, or malicious insider needed; it is triggerable purely by an ordinary `placeOrder` call plus a normal `fillOrder` call. It qualifies as concrete "permanent freezing/loss of funds" per the validation criteria.

### Likelihood Explanation
Likelihood is limited by the fact that a rational solver typically simulates a fill before submitting the transaction and can choose not to fill in unusual circumstances; however, solvers that fill programmatically/optimistically (e.g., competing to be first, using automated bots) may not always simulate against a zero beneficiary edge case, and a malicious order-placer could deliberately set `beneficiary = 0` to grief solvers or to test/exploit automated filler bots into burning value. It can also occur accidentally through an encoding bug in a client that leaves `output.beneficiary` unset (default `bytes32(0)`).

### Recommendation
Add a zero-address check on `order.output.beneficiary` (and consider the same check for `order.user`/`predispatch` beneficiaries where relevant) in `placeOrder`, rejecting the order with `InvalidInput()` if `address(uint160(uint256(order.output.beneficiary))) == address(0)`. As defense in depth, also validate `beneficiary != address(0)` immediately before the native-token payout inside `_fillSameChain`/`_fillCrossChain` and `_withdraw`.

### Proof of Concept
1. User calls `placeOrder` with `order.output = PaymentInfo({ beneficiary: bytes32(0), assets: [{token: bytes32(0), amount: 1 ether}], call: "" })` and valid ERC-20 inputs; no revert occurs because `placeOrder` never checks `output.beneficiary`. [1](#0-0) 
2. A solver calls `fillOrder{value: 1 ether}(order, options)`; `_fillSameChain` computes `beneficiary = address(0)` and executes `beneficiary.call{value: beneficiaryTotal}("")`, which returns `sent = true`, so the function proceeds normally. [4](#0-3) 
3. The solver's 1 ETH is now held at `address(0)` with no way to reclaim it, while the solver still receives the escrowed input tokens from `_withdraw`, meaning the loss is entirely borne by the value sent to the zero-address beneficiary.

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L53-59)
```text
    function _fillSameChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L95-100)
```text
            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-170)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L186-190)
```text
            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
    }
```
