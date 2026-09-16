### Title
Rebasable/elastic-supply tokens break IntentGateway's static escrow accounting, permanently freezing user funds after a negative rebase - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2`/`IntentsBase` escrows tokens by recording a fixed `uint256` amount per `(commitment, token)` pair in the `_orders` mapping at `placeOrder` time, and later pays that exact recorded amount out of the gateway's pooled token balance on `RedeemEscrow`/`RefundEscrow`. The contract already accounts for fee-on-transfer deviations by measuring actual `balanceOf` deltas at deposit time, but it never re-checks or reconciles balances at withdrawal time. For a rebasable/elastic-supply ERC20 (e.g. Ampleforth-style tokens) escrowed in the shared gateway contract, a negative rebase that occurs while multiple orders are pending will shrink the contract's actual token balance below the sum of all outstanding `_orders[...]` entries, causing later withdrawals to revert and permanently freezing those users' escrowed funds — the same root cause described in the external `LOB` report.

### Finding Description
`placeOrder` in `evm/src/apps/IntentGatewayV2.sol` transfers the input token into the gateway and stores the actual received amount in `order.inputs[i].amount`, which is committed into `_orders[commitment][token]` (see the fee-on-transfer handling at [1](#0-0) ). This value is a **snapshot** taken once, at deposit time — it is never revisited.

Withdrawal (used both for solver redemption via `RedeemEscrow` and user refunds via `RefundEscrow`) is implemented in `_withdraw`: [2](#0-1) 

This function reads `escrowed = _orders[body.commitment][token]` (the static recorded value) and calls `IERC20(token).safeTransfer(beneficiary, amount)` without ever comparing against the gateway's current actual `balanceOf(address(this))`. All orders for the same token share the same physical token balance inside the single `IntentGatewayV2` contract instance (there is no per-order segregated custody), so the accounting invariant "sum of all `_orders[*][token]` == `balanceOf(gateway)`" is only true at the moment tokens are deposited.

If the escrowed token is rebasable (its holders' balances change automatically with total supply, without any transfer), a negative rebase after deposit reduces `balanceOf(gateway)` while every `_orders[commitment][token]` entry for that token remains at its pre-rebase, un-adjusted value. Whichever withdrawal happens to be processed once the shortfall exists will succeed with tokens taken from balances "belonging" to other not-yet-settled orders, and eventually the last withdrawer(s) will call `safeTransfer` for an amount the contract no longer holds, causing a revert. Since `_withdraw` has no fallback, reconciliation, or pro-rata reduction logic, those users' escrow is stuck forever — a direct instance of the "internal records vs actual balance divergence" bug class from the `LOB` report, reachable simply by using a rebasable token as `order.inputs[i].token` in a normal, permissionless `placeOrder` call.

### Impact Explanation
This causes permanent freezing of user/solver funds: once a negative rebase drops the gateway's real token balance below the sum of recorded escrow entries, some legitimate order owners or solvers can never redeem or refund their full recorded escrow via `_withdraw`, and there is no governance or user-triggered mechanism in `IntentsBase`/`IntentGatewayV2` to reconcile the discrepancy. This meets the "permanent freezing of funds" bar for a Medium/High severity finding.

### Likelihood Explanation
Likelihood depends on whether a rebasable/elastic-supply token is ever listed as tradable input/output on a deployed `IntentGatewayV2` instance and whether a negative rebase occurs while orders remain outstanding — the code makes no distinction between rebasable and standard ERC20 tokens, and nothing in `placeOrder`/`fillOrder`/`cancelOrder` prevents a user from choosing such a token as `order.inputs[i].token`. Any state machine that lists such a token (common practice for cross-chain intent/DEX-style protocols) is directly exposed via ordinary user transactions.

### Recommendation
Either (a) explicitly disallow rebasable/elastic-supply tokens as escrowed assets (e.g., via an allow-list of supported input/output tokens vetted for standard, non-rebasing ERC20 behavior), or (b) change the escrow accounting to be balance-based rather than a static recorded amount — e.g., track escrow as a share of the contract's actual balance and recompute payouts from `IERC20(token).balanceOf(address(this))` at withdrawal time, proportionally reducing every outstanding order's entitlement when the contract's real holdings shrink, mirroring the recommendation in the referenced report.

### Proof of Concept
1. Deploy `IntentGatewayV2` and register a rebasable ERC20 token `R` (mintable/elastic supply, e.g., an Ampleforth-like token) as a supported input asset.
2. User A calls `placeOrder` with `order.inputs = [{token: R, amount: 1000}]`; `_orders[commitmentA][R] = 1000` is recorded and the gateway now holds `1000 R`.
3. User B calls `placeOrder` with a second order using the same token `R`, `amount: 1000`; `_orders[commitmentB][R] = 1000`, gateway now holds `2000 R`.
4. `R` undergoes a negative rebase of 50%; the gateway's `balanceOf(address(this))` drops to `1000 R`, while `_orders[commitmentA][R]` and `_orders[commitmentB][R]` are unchanged at `1000` each (total recorded = `2000`).
5. Solver fills order A; the cross-chain (or same-chain) settlement calls `_withdraw` for commitment A, which succeeds and transfers `1000 R` to the filler, draining the gateway's remaining balance to `0`.
6. Solver fills order B; `_withdraw` attempts `IERC20(R).safeTransfer(beneficiary, 1000)` but the gateway holds `0 R` — the transfer reverts, and User B's/solver B's escrow is permanently unredeemable. [2](#0-1)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L292-322)
```text
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
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
