### Title
IntentGateway escrow redemption hardcodes the solver as beneficiary with no way to redirect a blacklisted address, permanently freezing escrowed funds - (File: evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`_fillCrossChain` in `ExtrinsicIntents.sol` builds the `RedeemEscrow` withdrawal request with the beneficiary hardcoded to `msg.sender` (the solver/filler), with no parameter letting the solver designate an alternate recipient address, mirroring the FootiumPrizeDistributor pattern where `claimERC20Prize` only allows `_to == msg.sender`.

### Finding Description
When a solver fills a cross-chain order on the destination chain, `_fillCrossChain` dispatches a `RedeemEscrow` message back to the source chain with the beneficiary fixed to the caller's own address: [1](#0-0) 

On the source chain, when Hyperbridge delivers this message, `onAccept` decodes the `WithdrawalRequest` and calls `_withdraw`, which transfers the escrowed input tokens directly to that fixed beneficiary address using `IERC20.safeTransfer`: [2](#0-1) 

There is no path anywhere in the fill flow for the solver to specify a different recipient for the escrowed input tokens. If the solver's address is later blacklisted by the ERC20 contract governing the input token (e.g. USDC, USDT — both commonly used as intent inputs), `safeTransfer(beneficiary, amount)` reverts unconditionally, since `beneficiary` is baked into the on-chain `WithdrawalRequest` that Hyperbridge delivers, not a parameter the solver can adjust after the fact.

### Impact Explanation
`onAccept` is invoked directly by the Hyperbridge host when delivering the `RedeemEscrow` message; a revert there leaves the message undelivered/re-triable, but every retry hits the exact same hardcoded beneficiary and fails identically. Because `_orders[commitment][token]` is only decremented on a successful transfer, the escrowed input tokens remain locked in the gateway contract indefinitely — a permanent freezing of solver funds with no governance or user-level recovery path once the solver's address is blacklisted by the input token contract. This satisfies "permanent freezing of funds" via an unprivileged, single-transaction-reachable action (an intent solver simply calling `fillOrder`).

### Likelihood Explanation
Any solver interacting with `IntentGatewayV2`/`ExtrinsicIntents` is exposed the moment they fill an order whose input token is a blacklist-capable ERC20 (USDC/USDT and similar are explicitly supported as intent input assets per the documented fee/token model). No malicious actor is required — the solver's own address being sanctioned/blacklisted by the token issuer is sufficient, and this is a realistic real-world occurrence for widely used stablecoins.

### Recommendation
Allow the solver to supply a `recipient` distinct from `msg.sender` when filling a cross-chain order (analogous to adding a `recipient` argument in the referenced Footium fix), so the escrowed tokens' `WithdrawalRequest.beneficiary` can be redirected to an unblacklisted address instead of being permanently tied to the filler's own address at fill time.

### Proof of Concept
1. Solver `S` (an address destined to be blacklisted by the input token, e.g. USDC) calls `fillOrder` for a cross-chain order whose `order.inputs` include USDC escrowed on the source chain.
2. `_fillCrossChain` sets the `RedeemEscrow` beneficiary to `bytes32(uint256(uint160(msg.sender)))` = `S` (`ExtrinsicIntents.sol:209`).
3. USDC issuer blacklists `S` before Hyperbridge delivers the `RedeemEscrow` message to the source chain.
4. Hyperbridge delivers the message; `onAccept` → `_withdraw` calls `IERC20(USDC).safeTransfer(S, amount)`, which reverts because `S` is blacklisted (`IntentsBase.sol:468`).
5. Every subsequent delivery attempt fails identically since the beneficiary is immutably `S`; the escrowed USDC remains locked in the gateway with no way for `S` (or anyone) to redirect it to a working address.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
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
