This confirms a strong analog to the reported bug class.

### Title
Permanent freezing of escrowed intent funds when beneficiary is blacklisted by an ERC20 token (e.g. USDC) - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw` (used by `ExtrinsicIntents.onAccept` and mirrored in `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw`) pushes escrowed input tokens directly to a `beneficiary` address decoded from a cross-chain `WithdrawalRequest` via `IERC20(token).safeTransfer(beneficiary, amount)`. If that ERC20 (commonly USDC) has blacklisted the beneficiary, the transfer reverts.

### Finding Description
The settlement path is: a relayer delivers a `RedeemEscrow`/`RefundEscrow` POST request; `EvmHost.dispatchIncoming` performs a low-level `.call` to `onAccept` [1](#0-0) ; `ExtrinsicIntents.onAccept` decodes the `WithdrawalRequest` and calls `_withdraw` [2](#0-1) ; `_withdraw` unconditionally pushes tokens to the `beneficiary` with `IERC20(token).safeTransfer(beneficiary, amount)` [3](#0-2) .

`beneficiary` is either the solver (on `RedeemEscrow`) or the original order user (on `RefundEscrow`) — both are addresses the contract does not control and cannot force-clean from a blacklist. If USDC (or any blacklisting stablecoin) blacklists that address, `safeTransfer` reverts, `onAccept` reverts, and `EvmHost.dispatchIncoming` treats the whole delivery as failed, deleting the request receipt so it "can be retried" [1](#0-0) . Because the beneficiary's blacklist status doesn't change, every retry fails identically — the escrowed input tokens (and any accrued transaction fees, also pushed via `safeTransfer` in the same function [4](#0-3) ) are permanently stuck in escrow with no other function able to move them out. The same push-transfer pattern (there using raw `.call` + `TransferFailed` revert) appears in the Tron variant `withdraw` function [5](#0-4) .

This is structurally identical to the original report's root cause: settlement logic that force-pushes tokens to a possibly-blacklisted address inside a callback whose failure blocks the entire settlement/liquidation-equivalent flow, rather than allowing the affected party to claim funds separately (pull-over-push).

### Impact Explanation
For cross-chain orders, the escrowed input tokens on the source chain (and the destination-side output tokens the solver already paid) become permanently unrecoverable once the settlement message is delivered to a blacklisted beneficiary — no alternate withdrawal path exists in `_withdraw`/`withdraw`. This is a concrete permanent freezing-of-funds vulnerability affecting user or solver escrow, satisfying High impact per the validation criteria (unbacked freeze of user/solver funds, route unable to deliver value).

### Likelihood Explanation
Low-to-moderate likelihood: it requires the beneficiary address (order user or solver) to be blacklisted on a compliance-gated ERC20 like USDC. This can happen incidentally (a user/solver gets blacklisted after placing/filling an order) or could be induced adversarially by a malicious solver deliberately using a beneficiary address they know will get blacklisted, or by an attacker front-running to get a target user's collateral stuck. It does not require any privileged access — any ordinary user placing/filling an order can trigger the condition once the recipient becomes blacklisted.

### Recommendation
Adopt a pull-over-push pattern for `_withdraw`/`withdraw`: on `onAccept`, credit the beneficiary's balance in internal accounting instead of transferring immediately, and expose a separate `claim(token, amount)` function the beneficiary (or anyone on their behalf) can call to pull the tokens once able. Alternatively, wrap the `safeTransfer` call in a try/catch and, on failure, escrow the amount into a claimable mapping instead of reverting the whole `onAccept`/`withdraw` call, so message delivery (and finalization of `_filled`) still succeeds even if the token transfer to a blacklisted address fails.

### Proof of Concept
1. User places a cross-chain order via `IntentGatewayV2`/`ExtrinsicIntents.placeOrder`, escrowing USDC as `order.inputs`, with `order.user` (or a solver's `beneficiary`) being an address.
2. USDC issuer blacklists that beneficiary address (independently, e.g. due to unrelated compliance action) before settlement is delivered.
3. Solver fills the order on the destination chain; a `RedeemEscrow` (or `RefundEscrow` on cancellation) POST request is dispatched back to the source chain.
4. Relayer submits the proof; `EvmHost.dispatchIncoming` calls `ExtrinsicIntents.onAccept` → `_withdraw`, which calls `IERC20(usdc).safeTransfer(blacklistedBeneficiary, amount)` [6](#0-5) .
5. USDC's `transfer` reverts because the recipient is blacklisted; `onAccept` reverts; `EvmHost.dispatchIncoming` catches the failure and deletes the request receipt, allowing indefinite retries that all fail identically [1](#0-0) .
6. The escrowed USDC remains locked in the `IntentGateway`/`ExtrinsicIntents` contract permanently, with no alternative claim mechanism.

### Citations

**File:** evm/src/core/EvmHost.sol (L809-816)
```text
        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-477)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
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
