### Title
Escrow release permanently reverts when the beneficiary cannot accept a raw native-token `call` transfer, freezing escrowed native-token funds - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._sendValue` (used by `IntentsBase._withdraw` and by the cross-chain fill/refund paths in `ExtrinsicIntents.sol` / `IntrinsicIntents.sol`) unconditionally transfers native tokens via a raw `.call{value: amount}("")` and reverts the entire transaction with `InsufficientNativeToken` if that call is unsuccessful. Because the `beneficiary` address is attacker/user-controlled (`order.user`, `order.output.beneficiary`, or `msg.sender`), and there is no ERC-165/receiver-capability check or graceful fallback (unlike the sibling `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` contracts, which explicitly fall back to an ERC-20 transfer when a native push fails), this mirrors the `FathomProxyWalletOwner` bug class: the code assumes an arbitrary destination address will always be able to receive raw-call native value.

### Finding Description
`_sendValue` is defined as: [1](#0-0) 

It is the sole mechanism for releasing escrowed native tokens in `_withdraw`: [2](#0-1) 

`_withdraw` is invoked from `ExtrinsicIntents.onAccept` when Hyperbridge delivers a `RedeemEscrow` or `RefundEscrow` message from the destination chain back to the source-chain gateway: [3](#0-2) 

The `beneficiary` in this withdrawal request is either the solver (`msg.sender` at fill time) or `order.user` (set by the order creator when placing an order, and also used again in `_cancelFromDest`): [4](#0-3) 

If `beneficiary` is a smart-contract address without a `receive()`/payable `fallback()` (e.g., a multisig, vault, or any non-payable contract set as `order.user` or as `order.output.beneficiary`), the `.call{value: amount}("")` in `_sendValue` fails and `_withdraw` reverts with `InsufficientNativeToken`. Since `onAccept` is the host's designated entry point for this specific, deterministic message, and the message body (including the fixed `beneficiary`) never changes across retries, every future delivery attempt for that same commitment will also revert, in the same way `FathomProxyWalletOwner.closePositionFull`/`withdrawXDC` always fail once ownership is transferred to a contract without a `receive` method.

By contrast, the project's own `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` contracts explicitly handle this exact scenario by falling back to an ERC-20 transfer when the native push fails, precisely to avoid "permanently lock[ing] funds": [5](#0-4) 

`IntentsBase._withdraw` has no equivalent fallback for native-token escrow, so the analogous protection is missing there.

### Impact Explanation
Any order whose input token is the native asset (`token == address(0)`) and whose `order.user` (or, for same-chain/cross-chain fills, `order.output.beneficiary`) resolves to a contract that cannot accept a bare native-value call will have its escrowed native tokens permanently stuck once a `RedeemEscrow`/`RefundEscrow` message is dispatched: `_withdraw` will revert on every delivery attempt, `onAccept` will never succeed, and the escrow can never be released. This is a permanent freezing of user/solver funds reachable from a single order placement/cancellation by an ordinary, unprivileged actor (the order creator chooses `order.user`; a solver could similarly be a contract without a payable fallback). It also blocks the relayer from ever completing delivery of that specific commitment, effectively creating an undeliverable route for that message.

### Likelihood Explanation
Likelihood is significant because `order.user` and `order.output.beneficiary` are fully attacker/user-controlled `bytes32`-encoded addresses with no validation that they can accept raw ETH transfers, and many legitimate smart-contract wallets, vaults, or multisigs (or a simple minimal proxy without a `receive()`) do not implement a payable fallback. A user or integrator could inadvertently (or a malicious actor deliberately, to grief a solver/protocol) set such an address as the beneficiary of a native-token order, permanently locking the corresponding escrow.

### Recommendation
Apply the same defensive pattern already used in `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable`: when the native `.call` in `_sendValue` fails, fall back to wrapping the native asset (e.g., WETH) and delivering it as an ERC-20 transfer to the beneficiary instead of reverting the whole withdrawal. Alternatively, implement a pull-based withdrawal pattern for native-token escrow (credit an internal balance the beneficiary can later claim) so a single failed push can never permanently block escrow release.

### Proof of Concept
1. An order creator submits a cross-chain order via `IntentGatewayV2`/`IntrinsicIntents`/`ExtrinsicIntents` with `order.inputs[i].token == address(0)` (native asset) and `order.user` set to the address of a deployed contract that has neither a `receive()` nor a payable `fallback()` function.
2. The order is filled on the destination chain and a `RedeemEscrow` (or the order is cancelled, dispatching `RefundEscrow`) message is relayed back to the source-chain gateway.
3. `ExtrinsicIntents.onAccept` decodes the `WithdrawalRequest` and calls `IntentsBase._withdraw`, which calls `_sendValue(beneficiary, amount)`.
4. `beneficiary.call{value: amount}("")` reverts because the beneficiary contract has no payable receive/fallback; `_sendValue` reverts with `InsufficientNativeToken`, reverting the whole `onAccept` transaction.
5. Every subsequent relayer resubmission of the same message hits the identical code path and reverts identically — the escrowed native tokens are permanently unrecoverable through the intended protocol flow.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-306)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-324)
```text
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
