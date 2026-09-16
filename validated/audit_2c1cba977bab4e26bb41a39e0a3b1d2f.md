### Title
Duplicate input tokens in `IntentGatewayV2.placeOrder` merge into one escrow bucket, enabling over-release of escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron deployment of `IntentGatewayV2` escrows order inputs with `_orders[commitment][token] += reducedInputs[i].amount;` and performs no check for duplicate input tokens in a single order. This is the same bug class as the `DistributionRecord` issue: several logically distinct leaves (here, distinct `order.inputs[i]` entries) collapse into a single accounting key (`_orders[commitment][token]`), so downstream code that iterates per-leaf can release/decrement against the merged bucket more than once. The mainline EVM `IntentGatewayV2.sol` was already hardened against exactly this by rejecting duplicate input tokens at `placeOrder`, but the Tron variant was not updated to match.

### Finding Description
`placeOrder` in the Tron contract accepts an `Order` with an arbitrary `inputs` array and, for each input, adds its (fee-reduced) amount into the escrow map keyed only by `(commitment, token)`: [1](#0-0) 

If a user submits an order with two input entries for the same token (e.g. `USDC` appearing twice), both amounts are summed into the *same* `_orders[commitment][USDC]` slot instead of being rejected. The commitment hash is computed over the full `order` struct including the duplicated entries, so the order is otherwise valid and unique.

Compare this to the main EVM `IntentGatewayV2.sol`, which explicitly guards against this: [2](#0-1) 

The regression test for the EVM fix documents the exact failure mode this guard prevents: [3](#0-2) 

Release of escrowed funds happens in the shared `IntentsBase._withdraw`, which iterates the `WithdrawalRequest.tokens` list (built to mirror `order.inputs`) and decrements the same `_orders[commitment][token]` slot once per list entry: [4](#0-3) 

Because the escrow bucket for a duplicated token is a single merged sum, and the release/refund path is driven by a token list that can independently repeat the same token (mirroring the duplicate `order.inputs`), the same underlying escrow can be decremented and paid out multiple times against entries that were never separately escrowed — precisely the "multiple leaves collapse into one key" accounting bug described in the `DistributionRecord` report, where multiple valid entries sharing a key cause the total to be tracked incorrectly and allow either loss or, as documented by the fixed EVM regression test, *over-release* of the escrow.

### Impact Explanation
An attacker (any unprivileged order placer) can craft an order with duplicate input tokens to manipulate how much is escrowed vs. how much is later released. The EVM codebase's own regression test title — "same-chain partial fills over-release repeated input escrow" — confirms this exact bug class previously allowed a solver/filler to receive more escrowed tokens than were actually deposited, i.e., a direct theft of gateway funds. The Tron contract, which mints/burns and moves real value on the Tron side of the bridge, has not received the equivalent fix, leaving it exposed to the same class of fund-draining bug on an unprivileged, single-transaction path (`placeOrder` → `fillOrder`/cross-chain `onAccept` → `_withdraw`).

### Likelihood Explanation
High. `placeOrder` is a fully permissionless, single-transaction entry point with no validation against duplicate tokens in `order.inputs`. No special privileges, timing, or governance action is required — a user only needs to submit an order whose `inputs` array repeats a token address, then have any solver fill/redeem it through the standard flow.

### Recommendation
Port the same defensive check already present in `evm/src/apps/IntentGatewayV2.sol` (`if (_orders[commitment][token] != 0) revert InvalidInput();` before writing to `_orders[commitment][token]`) into `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `placeOrder`, for both the predispatch and non-predispatch escrow loops, so that orders with duplicate input tokens are rejected instead of merged into a single escrow bucket.

### Proof of Concept
1. Attacker calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs = [ {token: USDC, amount: X}, {token: USDC, amount: Y} ]`.
2. `_orders[commitment][USDC]` is set via `+=` to `X' + Y'` (fee-reduced sum), with no revert, unlike the patched EVM contract.
3. The order is filled cross-chain / same-chain; the resulting `WithdrawalRequest.tokens` (constructed to mirror `order.inputs`) can list `USDC` twice with amounts corresponding to each original leg.
4. `IntentsBase._withdraw` (shared library logic) processes the token list entry-by-entry, decrementing the same merged `_orders[commitment][USDC]` bucket per entry — this is the exact mechanism the EVM regression test `testRevert_PlaceOrder_DuplicateInputTokens` was written to prevent by rejecting the order at placement time rather than relying on withdrawal-side correctness.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-464)
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

```

**File:** evm/src/apps/IntentGatewayV2.sol (L364-373)
```text
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2115-2121)
```text
    /// @notice Placing an order with duplicate input tokens must revert.
    /// Regression test for: same-chain partial fills over-release repeated input escrow.
    function testRevert_PlaceOrder_DuplicateInputTokens() public {
        // Two input legs both using USDC — this previously merged into one escrow bucket
        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1200 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});
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
