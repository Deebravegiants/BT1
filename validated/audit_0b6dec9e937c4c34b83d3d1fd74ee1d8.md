### Title
Atomic multi-token `_withdraw`/`withdraw` release blocks all other escrowed tokens and fees if one token transfer reverts - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw` (and its Tron counterpart `IntentGatewayV2.withdraw`) releases *all* of an order's escrowed output tokens plus the accumulated protocol/relayer fee token in a single atomic loop. If the transfer of just one of those assets to the beneficiary reverts, the entire release reverts, so none of the other (perfectly fine) tokens or the fee payout can be claimed. This mirrors the reported `claimRewards` bug class: two logically independent "claim" paths (per-token escrow release vs. fee release, and release of token A vs. token B) are coupled into one all-or-nothing call.

### Finding Description
`_withdraw` in `IntentsBase.sol` iterates `body.tokens` and transfers each escrowed token to the beneficiary, then (when `finalize` is true) also transfers the accumulated transaction-fee token: [1](#0-0) 

The Tron deployment's `IntentGatewayV2.withdraw` has the identical structure: [2](#0-1) 

This function is reachable by any relayer delivering a valid ISMP proof:
- `onAccept` for `RedeemEscrow`/`RefundEscrow` requests from a connected chain instance [3](#0-2) 
- `onGetResponse` for a cross-chain cancellation confirmation [4](#0-3) 
- permissionless same-chain `cancelOrder` [5](#0-4) 

Because both the per-token loop and the fee release live in the same function, and `IERC20.safeTransfer`/the low-level `token.call` used for each token must all succeed for the transaction to commit, a single problematic token (a blacklist-capable stablecoin such as USDT/USDC blacklisting the beneficiary, a pausable token, a deflationary/fee-on-transfer token whose accounting the escrow doesn't expect, or a token that simply reverts) blocks:
1. Release of every *other* legitimate escrowed token in the same order.
2. Release of the accumulated Hyperbridge/protocol transaction fee token, even though it is unrelated to the failing token.

`EvmHost.dispatchIncoming` does catch a reverting `onAccept`/`onGetResponse` call and deletes the request receipt so the message can be retried later: [6](#0-5) 

This makes *transient* failures retryable, but does not help when the failure condition is permanent (e.g., the beneficiary address is durably blacklisted on one of the escrowed tokens or on the fee token, or the token contract is permanently paused/frozen). In that case, retries will always hit the same revert, and none of the order's assets — including the tokens that have nothing wrong with them — can ever be released, since `_orders`/`_filled` state changes are rolled back together with the failing transfer.

### Impact Explanation
A single unrelated/blacklisted/malicious token included among an order's outputs (or the beneficiary being blacklisted on the fee token) permanently freezes **all** other escrowed assets and the transaction fee for that order, denying the beneficiary funds they are otherwise fully entitled to. This is a concrete freezing-of-funds impact analogous to the referenced `claimRewards` finding, satisfying the "permanent freezing of funds" acceptance criterion, and is reachable from ordinary user/solver flows (order placement, fill, cancel) without any privileged role.

### Likelihood Explanation
Likelihood is realistic: intent orders can escrow arbitrary ERC-20 tokens supplied by the order creator, including tokens with blacklist/pause functionality (USDT, USDC) or tokens deliberately crafted to revert for specific addresses. A beneficiary that becomes blacklisted on any single output token (their own doing, e.g., sanctioned address, or targeted griefing) is sufficient to trigger the block; no attacker collusion with the protocol is required.

### Recommendation
Decouple token releases so that a revert on one asset cannot block the others, following the same pattern recommended in the source report: iterate defensively (e.g., wrap each token transfer in a try/catch or low-level call and track/skip failures individually, persisting the still-escrowed amount for the failing token so it can be swept/retried separately), and release the transaction fee independently of the per-token escrow loop rather than gating it on the full loop's success.

### Proof of Concept
1. User places an order whose `output.assets` include a normal token `A` and a blacklist-capable token `B` (e.g., USDT), with the fee token being `C`.
2. Before the fill/cancel is settled, the beneficiary address becomes blacklisted on token `B` (or `B` is a token intentionally designed to revert transfers to certain addresses).
3. A relayer delivers the `RedeemEscrow`/`RefundEscrow` POST request; `onAccept` calls `withdraw`/`_withdraw`.
4. The loop successfully transfers token `A`, but the transfer of blacklisted token `B` reverts inside the same atomic call.
5. The whole `withdraw`/`_withdraw` call reverts; `EvmHost.dispatchIncoming` catches it and deletes the receipt for a retry, but every retry hits the same permanent blacklist condition.
6. Token `A` (fully transferable) and the fee token `C` are now permanently locked in `_orders[commitment][...]`, unrecoverable through any code path, even though nothing is wrong with them.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-485)
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

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-539)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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
        }

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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
