I have sufficient evidence to construct the analog finding.

### Title
Escrow release via `RedeemEscrow`/`RefundEscrow` uses push transfers incompatible with blocklisting tokens (e.g. USDC/USDT), permanently freezing escrowed funds - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
The IntentGatewayV2 escrow settlement path (`_withdraw`, invoked from `onAccept` when processing `RedeemEscrow`/`RefundEscrow` messages) pushes tokens directly to a `beneficiary` address derived from message data (the filling solver or the original order user) using `IERC20.safeTransfer`. If that beneficiary is on an admin-controlled blocklist of a token like USDC or USDT, the transfer reverts, the whole `onAccept` call reverts, and because `EvmHost.dispatchIncoming` simply deletes the request receipt to allow a retry, the exact same message will be resubmitted and fail identically forever — permanently freezing the escrowed funds.

### Finding Description
`IntentsBase._withdraw` iterates over the withdrawal request's token list and pushes tokens straight to the `beneficiary` computed from the message body: [1](#0-0) 

This is called by the cross-chain settlement handler on `RedeemEscrow` (fill payout to the solver) and `RefundEscrow`/GET-response cancellation (refund to `order.user`), both reachable from `onAccept`, which is invoked by `EvmHost.dispatchIncoming` on behalf of any relayer once a valid proof is delivered: [2](#0-1) 

The beneficiary address is embedded in the message: for `RedeemEscrow` it's `msg.sender` of the solver that called `fillOrder` on the destination chain, encoded into the withdrawal body at fill time: [3](#0-2) 

For refunds, it's the original order creator's address. Neither of these can be changed once the order is placed/filled — they are fixed values baked into the cross-chain message and its commitment hash. If the token being withdrawn (e.g. USDC or USDT) blocklists that beneficiary address, `IERC20(token).safeTransfer(beneficiary, amount)` at IntentsBase.sol:468 reverts unconditionally on every delivery attempt. Since `EvmHost.dispatchIncoming` only deletes the request receipt on failure — enabling indefinite retries with the identical calldata — the message can never be delivered successfully, and the escrowed input tokens (for `RedeemEscrow`) or refunded tokens (for `RefundEscrow`) are permanently stuck in the `IntentGatewayV2`/`ExtrinsicIntents` contract with no alternate withdrawal path. The equivalent push-transfer pattern also exists in the Tron variant's `withdraw` function. [4](#0-3) 

This mirrors the referenced report exactly: a vesting/escrow contract's forced push-transfer to an address that a token operator has blocklisted causes a permanent revert of the disbursement functionality, with no pull-based fallback.

### Impact Explanation
This is a High-impact issue: user or solver funds escrowed in the IntentGateway can become permanently frozen with no recovery mechanism, since the beneficiary in the withdrawal message is immutable once dispatched and the same failing call will be retried indefinitely. Both order fulfillment (solver payout) and order cancellation (user refund) paths are affected, meaning the freeze can hit either counterparty depending on who ends up blocklisted.

### Likelihood Explanation
Low-to-Medium: it requires (a) the escrowed/output token to implement an admin-controlled blocklist (true for USDC and USDT, both very commonly used tokens in DeFi and explicitly supported by this protocol given USDC test fixtures), and (b) the specific beneficiary address (solver or user) to be blocklisted by that token's issuer. This is realistic since IntentGatewayV2 is designed to move stablecoins like USDC/DAI across chains, and any solver or user address that becomes sanctioned/blocklisted after or during an in-flight order will trigger a permanent freeze of the associated escrow.

### Recommendation
Replace the push-transfer pattern in `IntentsBase._withdraw` (and the analogous `withdraw` function in `evm/tron/contracts/apps/IntentGatewayV2.sol`) with a pull-based claim mechanism: on `onAccept`, credit an internal balance mapping for the beneficiary instead of calling `safeTransfer` directly, and expose a separate `claim()`/`withdraw()` function that the beneficiary (or anyone, sending to the beneficiary) can call to pull the tokens out. This decouples message delivery success from the recipient's transfer eligibility, ensuring a blocklisted beneficiary only blocks their own claim rather than corrupting the whole cross-chain message delivery and permanently locking the funds.

### Proof of Concept
1. User places a cross-chain order on chain A escrowing 1000 USDC as input, expecting DAI output on chain B.
2. A solver fills the order on chain B, becoming `msg.sender` and thus the future `beneficiary` for `RedeemEscrow` back on chain A (`ExtrinsicIntents._fillCrossChain`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol:167-212`).
3. Before the `RedeemEscrow` message is relayed to chain A, Circle blocklists the solver's address on USDC (chain A's escrowed token).
4. A relayer delivers the proof; `EvmHost.dispatchIncoming` calls `onAccept`, which calls `IntentsBase._withdraw`, which calls `IERC20(USDC).safeTransfer(solver, 1000e6)` — this reverts because the solver is blocklisted.
5. `dispatchIncoming` catches the failure and deletes the request receipt, allowing indefinite resubmission of the identical message — but every resubmission reverts identically.
6. The 1000 USDC remains permanently escrowed in the `IntentGatewayV2` contract with no way for the solver, the user, or governance to retrieve it via the normal flow.

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

**File:** evm/src/core/EvmHost.sol (L794-818)
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
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
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
