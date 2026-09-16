### Title
Checks-Effects-Interactions violation in `withdraw()` allows reentrant double-redemption of escrowed order funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of the Intent Gateway's `withdraw()` function performs the native/ERC20 token transfer to the beneficiary **before** decrementing the corresponding escrow balance in `_orders`, reproducing the exact CEI ordering flaw described in the Y2K `mintDepositInQueue` report (external interaction precedes the state effect that should gate it). This differs from the hardened pattern already present in the main EVM `IntentsBase._withdraw` implementation, which decrements escrow *before* transferring.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the internal `withdraw()` function iterates over `body.tokens` and, for each entry:
1. Checks `_orders[body.commitment][token] == 0` (a presence check, not an amount check),
2. Immediately performs the external interaction — either a raw native value `.call{value: amount}("")` to `beneficiary`, or `token.call(...transfer...)` — and
3. Only *afterwards* decrements `_orders[body.commitment][token] -= amount`. [1](#0-0) 

Because `beneficiary` is attacker-controlled (it is derived from `order.output.beneficiary` for fills, or `order.user` for refunds — both are supplied at order-placement time and settled later via `onAccept`/`onGetResponse`), a malicious contract configured as beneficiary can execute arbitrary code inside its `receive()` fallback (for the native-ETH branch) during step 2, before the escrow balance for that token has been reduced. In the equivalent, already-fixed main EVM contract, the corresponding decrement happens *before* the transfer: [2](#0-1) 

showing that the project itself treats "decrement-before-transfer" as the correct, required ordering for this exact code path — and the Tron fork has regressed to the vulnerable ordering.

`withdraw()` is reached from `onAccept()` (an `onlyHost` ISMP callback processing `RedeemEscrow`/`RefundEscrow` messages) and from `onGetResponse()` (an `onlyHost` callback for cancellation proofs). Both are entry points driven by relayer-submitted proofs, i.e., reachable without special privilege via the normal cross-chain settlement/cancellation flow.

### Impact Explanation
If the host's inbound message/receipt bookkeeping (or any other reentrant call path back into `onAccept`/`onGetResponse` for the same order commitment) does not itself fully commit its "delivered" state before invoking the app callback, a malicious beneficiary can re-enter during the native-value callback and cause `withdraw()` to be executed again for the same `body.commitment`/token pair while `_orders[body.commitment][token]` still reflects the pre-transfer (undecremented) balance. This permits draining escrowed order funds beyond what was actually owed — a direct theft of user/solver escrow, matching the "Accept only concrete theft ... of funds" bar in the validation rules. Even absent a full double-delivery primitive, this ordering is a latent, unnecessary risk given the project's own hardened reference implementation demonstrates the safe ordering was known and intentionally applied elsewhere.

### Likelihood Explanation
Medium-to-High: `withdraw()` is only reachable through `onlyHost`-gated callbacks, so a single relayer-submitted proof delivery is required to trigger settlement, and the beneficiary/refund-recipient address is entirely attacker-chosen at order-placement time. The likelihood of a full double-spend depends on whether the ISMP host's request-receipt marking happens strictly before dispatching to the app (a property not verified within the scope of this Tron contract file), but the CEI violation itself is unconditionally present and reachable by any user who places an order with a contract-controlled beneficiary/refund address.

### Recommendation
Reorder the loop in `withdraw()` so that `_orders[body.commitment][token] -= amount` (and the fee-clearing `delete`) occurs **before** the external `.call` transfer, mirroring the pattern already used in `IntentsBase._withdraw`: [3](#0-2) 

Additionally, replace the "amount != 0" check with the actual amount so a zero-balance/zero-amount cannot spuriously pass, and consider adding `nonReentrant` to any state-mutating callback that ends in a native/token transfer to attacker-controlled recipients, consistent with `IntentGatewayV2.fillOrder`'s `nonReentrant` guard on the main EVM contract. [4](#0-3) 

### Proof of Concept
1. Attacker places (or is beneficiary of) an order whose output/refund beneficiary is a malicious contract with a `receive()` hook.
2. A relayer delivers the settlement message; `onAccept()`/`onGetResponse()` calls `withdraw()`.
3. Inside `withdraw()`'s loop, `beneficiary.call{value: amount}("")` transfers native funds to the malicious contract **before** `_orders[body.commitment][token] -= amount` executes: [5](#0-4) 
4. The malicious `receive()` hook attempts to re-trigger delivery/processing for the same order commitment (e.g., via any reentrant path into the host's message dispatch that has not yet finalized the first delivery's receipt).
5. Because `_orders[body.commitment][token]` has not yet been decremented, the reentrant call passes the same `_orders[...] == 0` check and can transfer the escrowed amount again, resulting in double payout from a single escrow deposit.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L443-443)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
```
