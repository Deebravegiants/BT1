### Title
Escrowed intent funds can be permanently frozen if the beneficiary is blacklisted by the escrowed token (e.g. USDC/USDT) - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw` (used by both cross-chain settlement via `ExtrinsicIntents.onAccept` and same-chain fills/cancellations via `IntrinsicIntents.sol`) always pushes escrowed tokens to a fixed `beneficiary` address derived from the order/commitment, using `IERC20.safeTransfer(beneficiary, amount)`. If that token implements an address blocklist (USDC, USDT, and similar centrally-administered stablecoins), and the beneficiary is or becomes blacklisted, the transfer permanently reverts, with no parameter to redirect funds to an alternate address.

### Finding Description
`_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` decodes the beneficiary from the `WithdrawalRequest.beneficiary` field and unconditionally transfers escrowed tokens to it: [1](#0-0) 

This function is reachable from:
- `ExtrinsicIntents.onAccept` for `RedeemEscrow` (beneficiary = solver who filled the order on the destination chain) and `RefundEscrow` (beneficiary = `order.user`) messages delivered cross-chain via Hyperbridge: [2](#0-1) 
- `IntrinsicIntents.sol`'s same-chain fill/cancel paths, where the beneficiary is either the filler (`msg.sender`) or `order.user`.

The Tron variant of the app, `IntentGatewayV2.sol`, has the identical pattern in `withdraw()`: [3](#0-2) 

Critically, when `onAccept` reverts because the underlying token transfer fails (e.g. `ERC20: transfer from/to blacklisted address` for USDC/USDT), `EvmHost.dispatchIncoming` swallows the failure and deletes the request receipt so the message "can be retried": [4](#0-3) 

This retry mechanism is designed for transient failures, but a token blacklist against the beneficiary address is not transient from the protocol's perspective — the message will fail identically on every retry attempt as long as that address remains blacklisted (which for USDC/USDT compliance blacklisting is typically permanent absent intervention by the issuer). Since neither `_withdraw`, `onAccept`, nor the `WithdrawalRequest` structure offers a way to specify or update an alternate recipient address, the escrowed collateral becomes permanently stuck in the `IntentsBase`/`IntentGatewayV2` contract with no on-chain recovery path — unlike the LayerZero endpoint adapter (`HyperbridgeLzEndpoint.onAccept`), which isolates a reverting downstream call in a `try/catch` and retains the payload for permissionless retry via `retryPayload` while still recording the delivery, the intents `_withdraw` path has no equivalent alternate-recipient recovery mechanism.

### Impact Explanation
Both users (cancellation/refund beneficiary) and solvers (redeem beneficiary) are unprivileged actors whose addresses are chosen at order-placement or fill time and are baked into the on-chain commitment. Escrowed input tokens for that specific order become permanently frozen in the `IntentGateway`/`IntentsBase` contract if the beneficiary address is later blacklisted by the escrowed token before settlement completes — the funds can never be delivered, matching the "permanent freezing of funds" acceptance criterion. This affects the escrowed principal amount of any order using a blacklist-capable ERC-20 as an input token, which can be material.

### Likelihood Explanation
Likelihood is realistic but not universal: it requires (a) an intent input token that supports centralized blacklisting (USDC, USDT are extremely widely used as intent inputs), and (b) the beneficiary address becoming blacklisted between order placement/fill and settlement delivery. Given the widespread use of USDC/USDT and the fact that blacklisting events do occur (sanctions, compliance actions, compromised addresses), this is a plausible medium-likelihood scenario, consistent with the original report's own risk classification.

### Recommendation
Add a pull-based claim mechanism for escrow withdrawals (analogous to the reporter's suggested `collectRedemption`-style pattern): instead of unconditionally pushing tokens to a hardcoded beneficiary inside `onAccept`/`_withdraw`, credit an internal claimable balance for the beneficiary and expose a separate `claim(token, to)` function that lets the beneficiary (or an address they control) pull funds to an address of their choosing. Alternatively, wrap the transfer in a try/catch within `_withdraw` and, on failure, escrow the amount into a per-beneficiary claimable mapping with a permissionless `rescue`/`redirect` function that allows specifying a different recipient address, mirroring the recovery pattern already used in `HyperbridgeLzEndpoint.retryPayload`.

### Proof of Concept
1. User places a cross-chain order with `inputs = [{token: USDT, amount: X}]`, escrowing USDT in `ExtrinsicIntents`/`IntentGatewayV2` on the source chain.
2. Before the solver's `RedeemEscrow` message is relayed and delivered, the intended beneficiary address (the solver, or the user in a cancellation/refund flow) gets blacklisted by USDT's issuer.
3. The relayer delivers the `RedeemEscrow`/`RefundEscrow` post request; `onAccept` → `_withdraw` calls `IERC20(USDT).safeTransfer(beneficiary, amount)`, which reverts because `beneficiary` is blacklisted.
4. `EvmHost.dispatchIncoming` catches the failure, deletes the request receipt, and returns — the message remains "retryable" per design, but every retry hits the identical blacklist revert.
5. The escrowed USDT for this commitment remains locked in the contract indefinitely, with no function available to redirect it to an unblocked address.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L794-817)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
```
