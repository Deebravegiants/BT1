### Title
Permanent Freezing of Escrowed Funds via Reverting `RedeemEscrow`/`RefundEscrow` Beneficiary in `IntentsBase._withdraw` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`IntentsBase._withdraw` releases escrowed native-token (`address(0)`) inputs via `_sendValue`, which reverts the whole call if the recipient's low-level `call` fails [1](#0-0) . This function is invoked from `onAccept`, which is itself dispatched by `EvmHost.dispatchIncoming(PostRequest, ...)` via an external `call` [2](#0-1) . The beneficiary for a `RedeemEscrow` message is fixed at fill time to `msg.sender` (the filling solver) and cannot be changed on retry [3](#0-2) . If that beneficiary address is a contract that always reverts on receiving ETH, delivery of the message will fail every single retry, permanently freezing the escrowed input tokens of the affected order with no recovery path in the contract.

### Finding Description
`_withdraw` iterates over all tokens for a `WithdrawalRequest` and, for native-token entries, calls the internal helper `_sendValue`:
```solidity
function _sendValue(address to, uint256 amount) internal {
  (bool sent,) = to.call{value: amount}("");
  if (!sent) revert InsufficientNativeToken();
}
``` [1](#0-0) 

This is invoked from `_withdraw`, which is called from `onAccept` for both `RedeemEscrow` and `RefundEscrow` message kinds:
```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    ...
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        _authenticate(incoming.request);
        WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
        return _withdraw(body, kind == RequestKind.RefundEscrow, true);
    }
``` [4](#0-3) 

The `beneficiary` for `RedeemEscrow` is encoded once, at fill time on the destination chain, as `msg.sender`:
```solidity
_post(
    order,
    _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
    options.relayerFee,
    nativeFee
);
``` [5](#0-4) 

Since `msg.sender` (the filler) can be any contract address the caller controls, an attacker can deploy a contract with no `receive`/payable `fallback` (or one that unconditionally reverts) and use it as the filler in `fillOrder`. On the source chain, `EvmHost.dispatchIncoming` delivers the `RedeemEscrow` message via a low-level `call` to `onAccept`; on failure it simply deletes the request receipt "so it can be retried" and returns silently:
```solidity
(bool success,) = address(destination)
    .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));
if (!success) {
    delete _requestReceipts[commitment];
    return;
}
``` [6](#0-5) 

Because the encoded beneficiary in the message body is immutable, every retry by any relayer will fail identically forever. Since `_withdraw` sets `_filled[body.commitment] = beneficiary` and decrements `_orders[...]` only if the whole call succeeds, an EVM revert rolls back all of these state changes atomically — the escrowed input tokens remain locked in the contract with `_orders[commitment][token]` never zeroed, and `_filled[commitment]` on the source chain never finalized. Because the destination side already marked the order `_filled[commitment] = msg.sender` at fill time, an `onGetResponse`-based cancellation from source (`_cancelFromSource`) will also fail with `Filled()` once queried, since the destination slot is non-empty — the affected order commitment has no remaining recovery path.

The identical pattern (`(bool sent,) = beneficiary.call{value: amount}(""); if (!sent) revert ...`) also appears in the Tron variant of the `IntentGatewayV2` contract's `withdraw` function [7](#0-6) .

### Impact Explanation
This permanently freezes the user's escrowed input tokens for any order filled by a solver contract engineered to reject ETH. There is no governance sweep or admin function that can reach `_orders[commitment][token]` for a stuck, unfinalized order — `SweepDust` only operates on protocol-level dust balances, not order-specific escrow [8](#0-7) . This satisfies the "permanent freezing of funds" / "route unable to deliver messages" impact criteria: the `RedeemEscrow` message can never be successfully delivered, and the associated escrow is stuck indefinitely.

### Likelihood Explanation
Reachable by any unprivileged actor acting as a solver/filler in the Intent Gateway flow — no special privileges are required to call `fillOrder`/`_fillCrossChain` with `msg.sender` set to a reverting contract. The only offsetting factor is that the filler forfeits their own claim to the input-token escrow, which reduces the *rational* attacker's motive (pure griefing/vandalism rather than profit), but the contract offers no defense or fallback (e.g., pull-payment pattern) regardless of intent, and accidental use of a non-payable-fallback contract as filler produces the same permanent lock.

### Recommendation
Adopt a pull-payment pattern for native-token escrow releases: instead of pushing ETH via `_sendValue` inside the atomic `_withdraw`/`onAccept` flow, credit an internal `withdrawable[beneficiary]` balance and let the beneficiary (or anyone on their behalf) claim it via a separate `withdraw()` call. This decouples cross-chain message delivery success from the recipient's ability/willingness to accept a push transfer, preventing a single reverting recipient from blocking `_filled` finalization and permanently freezing escrowed tokens. Alternatively, wrap the native-token leg in a try/catch so failures fall back to crediting a claimable balance instead of reverting the entire `_withdraw` call.

### Proof of Concept
1. Deploy `MaliciousFiller`, a contract with no payable `receive`/`fallback` (or one that always `revert()`s).
2. `MaliciousFiller` (or an EOA that then forwards calldata through it) calls `IntentGatewayV2.fillOrder(order, options)` on the destination chain for a legitimate cross-chain order, with `msg.sender == address(MaliciousFiller)`. Output tokens are delivered to `order.output.beneficiary` (the user), satisfying the fill; `_filled[commitment]` is set on the destination chain.
3. `_fillCrossChain` dispatches a `RedeemEscrow` POST request to the source chain with beneficiary hard-coded to `address(MaliciousFiller)` [3](#0-2) .
4. A relayer delivers the message to the source chain. `EvmHost.dispatchIncoming` calls `onAccept` → `_withdraw` → `_sendValue(MaliciousFiller, amount)`, which reverts because `MaliciousFiller` rejects ETH [1](#0-0) .
5. `EvmHost.dispatchIncoming` catches the failed low-level call, deletes the request receipt, and returns without reverting the outer transaction, allowing indefinite retries [6](#0-5) .
6. Every subsequent retry (by any relayer) fails identically since the beneficiary is immutable in the message body. `_orders[commitment][token]` is never decremented and `_filled[commitment]` on the source chain is never set — the user's escrowed input tokens are permanently stuck, and `_cancelFromSource` cannot recover them because the destination-side `_filled` slot is already non-empty.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L104-111)
```text
        /**
         * @dev Sweep accumulated protocol dust to a beneficiary.
         */
        SweepDust,
        /**
         * @dev Refund escrowed tokens to the user after a cross-chain cancellation.
         */
        RefundEscrow,
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-212)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-708)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }
```
