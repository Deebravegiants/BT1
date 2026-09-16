### Title
Blacklisted order beneficiary can permanently freeze escrowed cross-chain intent funds - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._withdraw`, invoked when a `RedeemEscrow`/refund message is delivered via `EvmHost.dispatchIncoming` → `IApp.onAccept`, transfers escrowed ERC20 tokens directly to the order's `beneficiary` (solver or user) with `IERC20(token).safeTransfer(beneficiary, amount)`. If the token is a blacklist-capable stablecoin (USDC/USDT) and the beneficiary address is blacklisted for that token, this transfer reverts every single time the message is retried, permanently freezing the escrowed input tokens for that order.

### Finding Description
`_withdraw` releases escrow to a beneficiary derived from message data supplied by the counterparty gateway (the solver's address on fill, or the user's address on refund/cancel): [1](#0-0) 

This function has no fallback path: on `safeTransfer` revert (e.g. token issuer blacklist), the whole call reverts. It is reached from the ISMP delivery path in `EvmHost.dispatchIncoming`, which calls the app's `onAccept` via a low-level `call` and, on failure, only deletes the replay-protection receipt "so that it can be retried": [2](#0-1) 

Because the retry replays the identical request (same beneficiary, same token, same amount), and a blacklist status does not change based on retries, every subsequent delivery attempt fails identically. There is no escrow-to-third-party fallback, try/catch, or alternate claim mechanism — the beneficiary field is fixed in the signed/committed order data and cannot be substituted. This mirrors the LiquidityManager.sol pattern in the referenced report: a direct, unconditional token push to a party the protocol does not control, with no escrow-of-last-resort if the recipient cannot receive funds.

The `RedeemEscrow`/refund flow reaching this code: [3](#0-2) 
also calls `_withdraw` from `IntrinsicIntents` same-chain fills and from cross-chain `onAccept` handling for `WithdrawalRequest` bodies, all of which route through the same unconditional `safeTransfer` to `beneficiary`.

### Impact Explanation
For any order whose destination-chain solver (fill beneficiary) or source-chain user (refund/cancel beneficiary) is blacklisted for the escrowed input token, the escrow can never be released: `RedeemEscrow` message delivery permanently reverts, and the escrowed funds sit frozen in the `IntentGateway`/`IntentsBase` contract indefinitely, with no admin or user recovery path since `_withdraw` is the only exit for escrowed balances. This is a permanent freezing-of-funds condition for that order — meets High severity per the accept criteria ("permanent freezing of funds").

### Likelihood Explanation
Requires the beneficiary (solver, in the common fill case) to be a blacklisted address for a censorable token like USDC/USDT — plausible if a solver's operating address is later sanctioned/blacklisted, or if a malicious order deliberately sets the output/beneficiary to a known-blacklisted address to grief a specific solver, or a user's own wallet becomes blacklisted before their refund settles. This does not require any privileged actor, only a normal `fillOrder`/`placeOrder`/`cancelOrder` submission by an ordinary user or solver, satisfying the "unprivileged... intent solver" reachability requirement.

### Recommendation
Wrap the `safeTransfer` call in `_withdraw` (and the equivalent paths in `IntrinsicIntents`/`ExtrinsicIntents`/`IntentGatewayV2` on Tron) in a try/catch (or low-level `call` with success check) per token transfer. On failure, route the funds into a per-beneficiary escrow/claim mapping (analogous to the fix recommended for LiquidityManager.sol) rather than reverting the whole withdrawal, and expose a separate `claim()` function so the affected party can withdraw to an alternate address, or so governance/relayer retries do not perpetually fail.

### Proof of Concept
1. User places a cross-chain order on the source chain via `IntentGatewayV2.placeOrder`, escrowing `USDC` as input.
2. A solver (or attacker crafting an order that names a blacklisted `beneficiary`) fills the order on the destination chain via `_fillCrossChain`, which dispatches a `RedeemEscrow` `WithdrawalRequest` back to the source chain naming the solver as `beneficiary`.
3. Assume the solver's address is later added to the USDC blacklist (e.g., due to unrelated sanction), or the order was crafted so `beneficiary` is already a blacklisted address.
4. Relayer proves and delivers the message; `EvmHost.dispatchIncoming` calls `onAccept` → `_withdraw`.
5. `IERC20(USDC).safeTransfer(beneficiary, amount)` reverts because `beneficiary` is blacklisted.
6. `dispatchIncoming` catches the revert, deletes `_requestReceipts[commitment]`, and returns — permitting a "retry", but any relayer resubmission replays the identical failing transfer.
7. The escrowed USDC remains locked in the gateway contract forever; the solver can never claim it and there is no alternate recovery path in `_withdraw`.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L200-220)
```text

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
    }
```
