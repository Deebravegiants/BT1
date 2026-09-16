### Title
Escrowed native-token withdrawals permanently revert (freezing funds) when the beneficiary is a contract without `receive`/`fallback` - (File: `evm/src/apps/intentsv2/IntentsBase.sol` / `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The IntentGatewayV2 escrow-release path (`RedeemEscrow`/`RefundEscrow`) pays out escrowed native tokens via a hardcoded, unconditional `beneficiary.call{value: amount}("")` and reverts the entire `onAccept` transaction if the call fails. Because the beneficiary address is fixed at order-creation/fill time and cannot be changed, a beneficiary that is a smart contract without a `receive`/payable `fallback` will cause this message to permanently and irrecoverably revert — freezing the escrowed funds forever, since no retry with a different address is possible.

### Finding Description
`IntentsBase._sendValue` and the tron variant's `withdraw` unconditionally attempt a raw native transfer and revert on failure with no fallback (e.g. wrapping to WETH) and no alternate recipient path: [1](#0-0) 

This is used inside `_withdraw`, which is invoked from `onAccept` on `RedeemEscrow`/`RefundEscrow` delivery: [2](#0-1) 

The tron/EVM-variant `IntentGatewayV2.sol` implements the same pattern directly in `withdraw()`, called from `onAccept`: [3](#0-2) [4](#0-3) 

The `beneficiary` field is set to `order.user` for a `RefundEscrow` (cancellation) and to the solver/filler address for a `RedeemEscrow` (successful fill) — both attacker/user-controlled or ordinary EOAs/contracts chosen by unprivileged actors when creating/filling an order: [5](#0-4) 

Because `onAccept` is invoked by the Hyperbridge message-delivery pipeline (`HandlerV2`/host `onAccept`) with no alternate beneficiary or retry mechanism, once such a beneficiary contract is set for an order with a native-token (`address(0)`) leg, every future relayer attempt to deliver that specific `RedeemEscrow`/`RefundEscrow` message will deterministically revert on the `.call{value:}`. The message can never be delivered/finalized, so the escrow entry in `_orders[commitment][token]` is never decremented and the underlying native tokens remain locked in the contract permanently — there is no admin sweep or alternate-recipient recovery path for this specific fund, unlike governance-controlled paths (`BandwidthManager.onAccept`'s `Withdraw` action, which is at least governance-set and can be corrected by re-issuing a new withdrawal to a different address).

### Impact Explanation
This results in permanent freezing of escrowed native-token funds: the specific order's escrowed ETH becomes irrecoverable because the sole withdrawal code path (`_withdraw`/`withdraw`) always targets the same fixed, unchangeable beneficiary address and has no fallback. This matches the "permanent freezing of funds" impact category. It is reachable purely through normal intents flow — a filler (solver) address, or an order's `user` address, that happens to be a smart-contract wallet/vault without a `receive` function (a very plausible real-world scenario, e.g. Gnosis Safe variants, timelocks, or vaults that reject bare value transfers by design) — no malicious governance or privileged role is required.

### Likelihood Explanation
Medium likelihood: this requires the beneficiary (order `user` or filling solver) to be a contract account without payable fallback, and the order's escrowed leg to include the native asset (`token == address(0)`). Given cross-chain intents commonly settle in native ETH and solvers/users increasingly operate through smart-contract wallets, this is a realistic and not purely theoretical scenario, but it does depend on that specific account-type combination rather than being unconditionally triggerable.

### Recommendation
Do not let a failed native transfer permanently brick the message. Options:
- Fall back to wrapping the native asset into WETH and crediting the beneficiary via ERC-20 `transfer` (which only requires the recipient to accept ERC-20 tokens, not raw ETH) when the raw `call` fails, mirroring common escrow-safety patterns.
- Alternatively, allow a pull-based recovery: on failed native `call`, credit an internal "unclaimed" balance for the beneficiary that can be withdrawn later (e.g. by permitting the beneficiary to specify an alternate recipient), rather than reverting `onAccept` and permanently blocking the request.

### Proof of Concept
1. A solver's on-chain address (or an order's `user` address) is a minimal smart contract with no `receive()`/payable `fallback()` (e.g., a bare multisig, vault, or a contract that intentionally rejects ETH).
2. The solver fills a cross-chain order whose input token is native ETH (`token == address(0)`), or the order's `user` cancels an order with native ETH escrowed.
3. The resulting `RedeemEscrow`/`RefundEscrow` ISMP message is dispatched to the source-chain `IntentGatewayV2`/`ExtrinsicIntents` gateway with `beneficiary` set to that contract address.
4. Any relayer's delivery of this message calls `onAccept` → `withdraw`/`_withdraw` → `beneficiary.call{value: amount}("")`, which reverts because the beneficiary rejects the value transfer.
5. Because `beneficiary` is immutably tied to this commitment and there is no alternate-recipient or WETH-fallback mechanism, every subsequent delivery attempt reverts identically — the escrowed native tokens for that commitment are permanently locked in the contract.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L587-600)
```text
        } else if (currentChain == orderDest) {
            // destination chain: dispatch RefundEscrow request to source chain
            // If order hasn't expired, only owner can cancel
            if (order.deadline >= block.number) {
                if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
            }

            // Mark as cancelled locally to prevent fills
            _filled[commitment] = address(uint160(uint256(order.user)));

            bytes memory body = bytes.concat(
                bytes1(uint8(RequestKind.RefundEscrow)),
                abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}))
            );
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
