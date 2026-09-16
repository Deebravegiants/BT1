## Analog Found

The reported bug class — an unconditional `safeTransfer`/`transfer` to a fixed recipient reverting the entire claim path if that recipient is blacklisted by the token (e.g. USDC) — has a direct, higher-impact analog in the Hyperbridge Intent Gateway's escrow settlement.

### Title
Blacklisted beneficiary permanently freezes escrowed order funds in IntentGateway settlement (`onAccept` → `_withdraw`) - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw()`, called from `onAccept()` when a `RedeemEscrow`/`RefundEscrow` message is delivered via Hyperbridge, performs `IERC20(token).safeTransfer(beneficiary, amount)` directly with no fallback, try/catch, or pull-payment mechanism. If the `beneficiary` address is on the token's blacklist (USDC/USDT-style tokens), the transfer reverts, the whole `onAccept` call reverts, and — because the beneficiary address is immutably encoded in the cross-chain message/commitment — there is no way to redeliver the message with a different recipient. The escrowed tokens are permanently stuck.

### Finding Description
`onAccept` on `ExtrinsicIntents.sol` decodes the `WithdrawalRequest` and calls `_withdraw(body, isRefund, true)` without any error handling: [1](#0-0) 

`_withdraw` then transfers each escrowed token straight to `beneficiary` via `safeTransfer`: [2](#0-1) 

The `beneficiary` is not attacker-supplied at redemption time — it is fixed inside the message body that was already dispatched and hashed into the order's `commitment`:
- For `RedeemEscrow`, the beneficiary is the solver address that called `fillOrder` (`bytes32(uint256(uint160(msg.sender)))`), baked into the message at fill time: [3](#0-2) 
- For `RefundEscrow` (cancel-from-destination), the beneficiary is `order.user`, fixed since order placement: [4](#0-3) 

Because the commitment/message is immutable once dispatched, if the token used for escrow (typically a stablecoin like USDC) blacklists the solver's or user's address after the order is placed/filled but before settlement is relayed, `onAccept` will revert every time it is retried — the message can never be successfully delivered, and the escrowed principal is permanently locked in the gateway with no admin sweep path for this specific stuck balance (sweep functions only cover protocol dust, not user/solver escrow).

The Tron variant has the same pattern using low-level `token.call(transfer(...))`, which similarly bubbles up `TransferFailed()`: [5](#0-4) 

The `WrappedHyperFungibleToken`/`Upgradeable` apps have the same unconditional `safeTransfer(beneficiary, ...)` pattern in their `onAccept`, meaning a blacklisted cross-chain transfer recipient permanently blocks delivery of that specific bridged-token message as well: [6](#0-5) 

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by any single relayed message: escrowed input tokens for a filled or cancelled order become irrecoverable once the fixed beneficiary is blacklisted by the escrowed ERC-20 (a realistic scenario for USDC/USDT which are common bridge assets). Unlike the original report (a griefing vector against a single withdrawer's *future* claims), here the funds themselves — the escrowed principal already locked in the contract — are permanently trapped with no retry or rescue path, since the beneficiary is committed on-chain and cannot be altered.

### Likelihood Explanation
Requires only that the fixed beneficiary (solver address for `RedeemEscrow`, or order placer for `RefundEscrow`) end up on the escrowed token's blacklist — a condition entirely outside the protocol's control and plausible for any long-lived solver/user address interacting with a centrally-blacklistable stablecoin. No privileged access is needed to trigger the freeze; it happens automatically once the address is blacklisted.

### Recommendation
Wrap the token transfer in `_withdraw` in a try/catch (or use a pull-based claim pattern) so that a reverting transfer credits the beneficiary's balance internally instead of reverting the whole settlement, allowing the beneficiary (or a substitute recipient) to claim tokens later, or allowing governance to redirect stuck escrow to an alternate address after a timeout.

### Proof of Concept
1. User places a cross-chain order escrowing USDC, `order.output.beneficiary = solverAddr`-independent (destination side).
2. Solver `S` fills the order on destination chain; `_fillCrossChain` dispatches `RedeemEscrow` with `beneficiary = S`.
3. Before the message is relayed and `onAccept` executes on the source chain, `S`'s address gets added to USDC's blacklist (Circle blacklists many addresses for various reasons).
4. Relayer submits the proof; `onAccept` → `_withdraw` calls `IERC20(usdc).safeTransfer(S, amount)`, which reverts because `S` is blacklisted.
5. Every subsequent relay attempt of the same message reverts identically — the escrowed USDC is permanently stuck in the `IntentGatewayV2`/`ExtrinsicIntents` contract, unrecoverable by governance sweep functions (which only target protocol dust, not order escrow).

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L301-306)
```text

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-324)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```
