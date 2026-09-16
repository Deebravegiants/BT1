Based on my investigation, I found the relevant analog.

### Title
Missing zero/burn-address validation on order beneficiary and cross-chain withdrawal recipients allows permanent loss of escrowed and solver funds - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
The OpenSea incident stemmed from a transfer path that let assets be sent to an uncontrolled/burn address with no upfront validation of the recipient. `IntentGatewayV2` and its base contracts have the same structural gap: `order.output.beneficiary` and `WithdrawalRequest.beneficiary` are raw `bytes32` values truncated to `address` via `address(uint160(uint256(...)))` with no `!= address(0)` (or code-existence) check anywhere in `placeOrder`, `fillOrder`, `_fillSameChain`, `_fillCrossChain`, or `_withdraw`.

### Finding Description
`_withdraw` in [1](#0-0)  derives `beneficiary` from an untyped `bytes32` and unconditionally calls `_sendValue(beneficiary, amount)` for native assets or `IERC20(token).safeTransfer(beneficiary, amount)` for tokens — neither path checks that `beneficiary != address(0)`. `_sendValue` itself only checks that the low-level call succeeded, and a plain value-call to `address(0)` (or any EOA-like non-existent address) succeeds, silently burning native funds: [2](#0-1) .

The same unchecked truncation pattern is repeated at every beneficiary/recipient touch-point:
- `_fillSameChain` and `_fillCrossChain` both compute `address beneficiary = address(uint160(uint256(order.output.beneficiary)));` with no validation before paying it out: [3](#0-2) .
- `placeOrder` never validates `order.output.beneficiary` before escrowing input tokens: [4](#0-3) .
- `_sweepDust` (governance-triggered) has the identical unchecked pattern: [5](#0-4) .

By contrast, `HyperFungibleToken._toAddr` at least validates the byte-length of the encoded address (reverting on malformed input) before minting/transferring, but it also performs no zero-address check: [6](#0-5) . For plain ERC-20 mint via OpenZeppelin's `_mint`, a zero recipient reverts internally, which happens to save that path — but `IntentGatewayV2`'s `safeTransfer`/`_sendValue` paths do not benefit from that internal safety net for native transfers or for any non-standard/legacy ERC-20 that omits OZ's zero-address check in `transfer`.

Because `order.output.beneficiary` is part of the order struct hashed into `commitment = keccak256(abi.encode(order))`, this is not attacker-forgeable by a third party after the order is placed — but exactly like the OpenSea case (where the underlying platform never validated the transfer destination before executing an irreversible action), a single unvalidated field flowing straight through to an on-chain payout is enough to convert a user/frontend/relayer bug (encoding error, wrong bytes32 padding, integration bug that leaves `beneficiary` as `bytes32(0)`) into a permanent, protocol-level fund loss with no recovery path, since `_filled`/`_orders` accounting is finalized regardless of whether the payout actually reached a controllable address.

### Impact Explanation
Any native-token or non-standard-ERC20 output/escrow payout addressed to `bytes32(0)` (or any other burn address) is unrecoverable: the escrow accounting (`_orders`, `_filled`) is updated as if the payout succeeded, so the order is marked filled/refunded and cannot be retried. This is a Medium-severity fund-loss/permanent-freezing bug reachable directly from `placeOrder`, `fillOrder`, and cross-chain `onAccept`/`onGetResponse` delivery of `RedeemEscrow`/`RefundEscrow` — no privileged role required.

### Likelihood Explanation
Likelihood is moderate: it requires a beneficiary field ending up as the zero address (or another burn/uncontrolled address) through client-side encoding bugs, ABI mismatches, or careless frontends/SDK integrations — the same class of "operator/tooling produced a bad address" root cause that caused the real-world OpenSea loss, rather than a deliberate protocol exploit by a third party. This is more likely for native-ETH outputs and any legacy ERC-20 whose `transfer` doesn't enforce a non-zero recipient (e.g., some older/non-compliant tokens integrated into `IntentGatewayV2`), matching the "Contract Vulnerability" bug class of the source report.

### Recommendation
Add an explicit `beneficiary != address(0)` (and ideally reject known dead/burn addresses) check in `placeOrder` before escrow, in `_fillSameChain`/`_fillCrossChain` before paying beneficiaries, and in `_withdraw`/`_sweepDust` before disbursing native or ERC-20 funds. Consider also validating that native-ETH beneficiaries are not contracts lacking a payable fallback in a way that would otherwise be masked by `_sendValue`'s generic revert.

### Proof of Concept
1. User (or a buggy integrating frontend) calls `placeOrder` with `order.output.beneficiary = bytes32(0)` and a native-ETH output asset (`token == address(0)`).
2. `placeOrder` escrows the input tokens without any validation of `beneficiary` ( [4](#0-3) ).
3. A solver calls `fillOrder`, which routes to `_fillCrossChain`; `beneficiary` decodes to `address(0)`, and `_sendValue(address(0), beneficiaryTotal)` succeeds, permanently burning the solver's ETH payment ( [3](#0-2) ).
4. The order is marked filled and a `RedeemEscrow` message is dispatched back to the source chain, which calls `_withdraw` to release the user's escrowed input tokens to the solver — completing the exchange even though the "output" leg was irreversibly destroyed ( [1](#0-0) ). No step in this flow reverts or flags the zero-address destination.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
    }
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L639-656)
```text
    function _sweepDust(SweepDust memory req) internal {
        uint256 outputsLen = req.outputs.length;
        for (uint256 i; i < outputsLen;) {
            TokenInfo memory info = req.outputs[i];
            address token = address(uint160(uint256(info.token)));
            uint256 amount = info.amount;

            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(req.beneficiary, amount);
            }
            unchecked {
                ++i;
            }
            emit DustSwept(token, amount, req.beneficiary);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L170-196)
```text
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-234)
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

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L328-334)
```text
    /// @notice Extracts an address from the first 20 bytes of a bytes memory value
    function _toAddr(bytes memory b) internal pure returns (address addr) {
        if (b.length != 20) revert InvalidAddress(b.length);
        // casting to 'bytes20' is safe because we already checked length
        // forge-lint: disable-next-line(unsafe-typecast)
        return address(bytes20(b));
    }
```
