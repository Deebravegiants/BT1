### Title
Blocklist-token beneficiary permanently freezes escrowed order funds in Intent Gateway `_withdraw` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw()` releases escrowed order tokens to a `beneficiary` address decoded directly from a cross-chain `WithdrawalRequest` (for `RedeemEscrow`/`RefundEscrow`) using a push `safeTransfer`. If the escrow token is a blocklist-capable ERC20 (e.g. USDC, USDT) and the beneficiary address is or becomes blocklisted, the transfer reverts, the entire `onAccept`/`onGetResponse` delivery reverts, and the escrowed tokens can never be released — there is no pull-based fallback or alternate beneficiary path.

### Finding Description
`_withdraw` is the single settlement path for both fills (`RedeemEscrow`, beneficiary = solver) and refunds/cancellations (`RefundEscrow`, beneficiary = original user), invoked from `onAccept` and `onGetResponse`: [1](#0-0) 

The transfer is a direct push `IERC20(token).safeTransfer(beneficiary, amount)` with no accounting-based pull mechanism. `beneficiary` comes from attacker/solver/user-controlled order data (`order.user`, or the solver's `msg.sender` at fill time), and is used verbatim on the receiving chain: [2](#0-1) 

Because `_withdraw` decrements `_orders[commitment][token]` and then calls `safeTransfer` in the same state-mutating call, and `onAccept` is `onlyHost` (called synchronously by the ISMP host when delivering the message), a revert in the transfer causes the entire delivery transaction to revert. Nothing is persisted — the escrow amount is not decremented and `_filled` is not set — so a relayer can retry, but the outcome is identical every time the beneficiary is blocklisted: permanent failure.

This mirrors the reported bug class exactly: a lending protocol's push-based repayment to a lender that could be blocklisted by USDC/USDT is analogous to the Intent Gateway's push-based escrow release to a solver/user that could be blocklisted, both lacking a pull/withdraw fallback.

### Impact Explanation
If the escrowed input token is a blocklist-capable stablecoin (USDC/USDT are explicitly supported/tested — see `usdc` usage throughout `IntentGatewayV2Test.sol`) and the intended recipient (solver on `RedeemEscrow`, or the order's original user on `RefundEscrow`/cancellation) is later added to that token's blocklist — whether by the issuer for compliance reasons, or self-inflicted/griefed by a third party who sends the token to a sanctioned address and gets flagged — the escrowed funds become permanently locked in the `IntentGatewayV2`/`IntentsBase` contract. Neither the solver, the user, nor governance has any alternate path to retrieve the escrowed principal, since `_withdraw` is the only release mechanism and it always pushes to the same fixed `beneficiary` recorded in the order/withdrawal request. This is a permanent freezing of user/solver funds.

### Likelihood Explanation
Requires only that the designated beneficiary (order user or solver) becomes blocklisted on a centrally-administered stablecoin used as an escrow input — a realistic, externally-triggered event for USDC/USDT-denominated cross-chain intents, not requiring any privileged action within Hyperbridge itself. A solver could also intentionally use a blocklist-affected address to grief another party's refund, or self-target to hold protocol dust hostage, but even the purely passive/organic case (existing customer gets blocklisted after placing an order) is sufficient to trigger irreversible fund lock.

### Recommendation
Replace the direct push `safeTransfer(beneficiary, amount)` in `_withdraw` with an accounting-based pull pattern: on failure (or by design) credit an internal claimable balance keyed by `(beneficiary, token)` and let the beneficiary call a separate `claim()`/`withdraw()` function themselves, or allow specifying an alternate receiving address. At minimum, wrap the transfer in a try/catch so a blocklist revert credits an internal claimable balance instead of reverting the whole settlement, preventing one frozen beneficiary from blocking their own (and no one else's) escrow release indefinitely.

### Proof of Concept
1. User places a cross-chain order on the source chain, escrowing `1000 USDC` via `placeOrder`, with `order.user` set to `Alice`.
2. Solver fills the order on the destination chain and the contract dispatches a `RedeemEscrow` `WithdrawalRequest{beneficiary: solverAddr}` back to source, per `_fillCrossChain` in `ExtrinsicIntents.sol` (lines 164-220).
3. Before the message is delivered, `solverAddr` is added to USDC's blocklist (e.g., regulatory action).
4. Relayer delivers the message; `onAccept` calls `_authenticate` then `_withdraw(body, false, true)`.
5. `_withdraw` calls `IERC20(usdc).safeTransfer(solverAddr, 1000e6)`, which reverts because USDC blocks transfers to a blocklisted address.
6. The entire `onAccept` call reverts; `_orders[commitment][usdc]` remains unchanged and `_filled[commitment]` is never set.
7. Every retry of the same message by any relayer reverts identically — the escrowed 1000 USDC is permanently stuck in the `IntentGatewayV2` contract with no recovery path, exactly analogous to the reported TellerV2 issue where a blocklisted lender permanently blocks loan repayment. [1](#0-0) [2](#0-1)

### Citations

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```
