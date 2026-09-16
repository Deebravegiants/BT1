### Title
Order beneficiary/token identifiers are silently truncated from `bytes32` to `address` without validating that the discarded high bytes are zero - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentGatewayV2`/`IntentsBase` stores order beneficiaries and token identifiers as `bytes32` (to support non-EVM destinations such as Substrate 32-byte `AccountId`s) and converts them to a 20-byte EVM `address` with `address(uint160(uint256(x)))`. Just like the ENS `hexToAddress` bug that truncated an oversized/malformed hex value to the last 20 bytes instead of rejecting it, this cast silently drops the high 12 bytes of any `bytes32` value instead of checking that they are zero, so a malformed or wrongly-encoded 32-byte identifier resolves to a different, unintended `address` rather than reverting.

### Finding Description
`IntentsBase._withdraw`, `IntentsBase._execute`, and `IntentsBase._sweepDust` all perform this unchecked truncation: [1](#0-0) [2](#0-1) [3](#0-2) 

`body.beneficiary`, `body.tokens[i].token`, and `order.output.assets[i].token` are `bytes32` values that travel cross-chain in the order/withdrawal payload (from `placeOrder` on the source chain through Hyperbridge dispatch to `onAccept`/`fillOrder` on the destination chain, or vice versa for `RedeemEscrow`/`RefundEscrow`). Because Hyperbridge is a cross-VM protocol where the same field width (`bytes32`) is reused to carry both 20-byte EVM addresses and 32-byte Substrate `AccountId`s, any code path that decodes such a value and truncates it via `uint160(uint256(...))` cannot distinguish "a correctly zero-padded EVM address" from "a genuine 32-byte account whose low 20 bytes happen to collide with a different address" or from a caller/relayer/upstream bug that puts non-zero bytes in the high 12 bytes. Unlike `ExtrinsicIntents._authenticate`/`IntentGatewayV2.authenticate`, which do check `request.from.length != 20` before casting, and unlike `EvmHost._bytesToAddress`/`HyperFungibleToken._toAddr`, which explicitly `revert` on any length other than 20, these three `IntentsBase` functions perform the numeric truncation unconditionally and accept it as valid.

### Impact Explanation
If a beneficiary or token identifier field is delivered with non-zero high bytes (whether from a genuinely non-EVM-shaped 32-byte value, an off-by-format encoding bug in a relayer/SDK, or any upstream component that fails to fully validate/zero-pad addresses before dispatch), `_withdraw` will silently release escrowed tokens to an address that is not the one actually intended, and `_sweepDust`/`_execute` will silently target the wrong ERC-20 contract or beneficiary. Funds routed to an unintended address recovered this way are effectively lost to the rightful recipient (permanent loss/freezing of funds from the intended party's perspective), with no revert or on-chain signal that a malformed identifier was processed.

### Likelihood Explanation
Low-to-moderate: like the original ENS finding, this requires an already-malformed/wrong-format 32-byte value to reach these functions (e.g., from an SDK/relayer bug, or a caller who unintentionally supplies a non-zero-padded value believing it will be validated). Hyperbridge's explicit multi-VM design (EVM 20-byte addresses vs Substrate 32-byte AccountIds sharing the same `bytes32` field) increases the chance of such a value being produced without malicious intent, compared to a pure single-VM system.

### Recommendation
Mirror the ENS-recommended fix and the pattern already used elsewhere in this codebase (`EvmHost._bytesToAddress`, `HyperFungibleToken._toAddr`, `ExtrinsicIntents._authenticate`): before truncating, require that the high 12 bytes of the `bytes32` are zero (e.g., `require(uint256(x) >> 160 == 0)`), reverting instead of silently truncating, in `_withdraw`, `_execute`, and `_sweepDust`.

### Proof of Concept
1. Construct an order/withdrawal payload where `beneficiary` (or `tokens[i].token`) is a `bytes32` value whose high 12 bytes are non-zero, e.g. `0x0102030405060708090a0b0c` + `<20-byte address>`.
2. Deliver this payload through the normal `onAccept`/`fillOrder` path so it reaches `IntentsBase._withdraw`.
3. `address(uint160(uint256(body.beneficiary)))` at [4](#0-3)  silently resolves to the low-20-byte address, and escrowed tokens are transferred there without any revert, even though the supplied identifier was not a valid, zero-padded EVM address.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-458)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L507-509)
```text
        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L639-647)
```text
    function _sweepDust(SweepDust memory req) internal {
        uint256 outputsLen = req.outputs.length;
        for (uint256 i; i < outputsLen;) {
            TokenInfo memory info = req.outputs[i];
            address token = address(uint160(uint256(info.token)));
            uint256 amount = info.amount;

            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
```
