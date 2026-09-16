### Title
Checks-Effects-Interactions violation in `IntentGatewayV2.withdraw` allows attacker-controlled beneficiary to execute code before escrow accounting is updated - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`withdraw()` in `IntentGatewayV2.sol`, which releases escrowed order funds on `RedeemEscrow`/`RefundEscrow` processing, sends native ETH to `beneficiary` via a low-level `.call{value: amount}("")` and only decrements the corresponding `_orders[commitment][token]` escrow accounting *after* that external call returns. `beneficiary` is derived from `order.user`, a value fully controlled by the unprivileged actor who created the order, and the contract has no reentrancy guard.

### Finding Description
In `withdraw()`:
```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    ...
}
_orders[body.commitment][token] -= amount;
``` [1](#0-0) 

the escrow debit (`_orders[commitment][token] -= amount`) happens strictly after the low-level ETH transfer to `beneficiary`. `beneficiary` is set from `order.user`/`body.beneficiary` in the `cancelOrder`/withdrawal flow (`beneficiary: order.user`) [2](#0-1) , a field entirely controlled by whoever placed the order — i.e. an unprivileged intent creator, not a trusted party. Because `beneficiary` can be an arbitrary contract, its `receive()`/fallback executes attacker-controlled code synchronously during the `.call{value:...}` in `withdraw()`, while `_orders[body.commitment][token]` for that entry (and for any subsequent tokens still being processed in the same `body.tokens` loop) has not yet been decremented.

`withdraw()` is only invoked internally from `onAccept` (gated `onlyHost`, for `RedeemEscrow`/`RefundEscrow` after `authenticate()`) [3](#0-2)  and from `onGetResponse` (also `onlyHost`) [4](#0-3) . No `nonReentrant` modifier is present anywhere in this contract.

This is the same bug class as the referenced Sherlock report (unrestricted low-level `.call{value:}` transfer to an externally-controlled address), but here it is compounded by a genuine check-effects-interactions ordering violation on escrow accounting rather than merely a "use safer transfer" style nit.

### Impact Explanation
If the host's message-processing/commitment-deduplication does not finalize/mark the incoming request as consumed strictly before invoking `onAccept`/`onGetResponse` (i.e. if any reentrant call back into the ISMP host during the attacker's fallback could cause a second dispatch into this same `withdraw()` call path for the same or a related commitment before `_orders` is decremented), the attacker could redeem escrowed funds more than once, resulting in direct theft of escrowed order funds from `IntentGatewayV2`. Even absent a provable double-spend through the host, the pattern is a bona fide CEI violation in a funds-release path keyed on attacker-controlled data (`order.user`), and it also allows an attacker's contract to consume unbounded gas / perform arbitrary state-changing reentrant calls elsewhere in the protocol at the exact moment `_orders` accounting for the beneficiary's own commitment is stale.

### Likelihood Explanation
The `beneficiary` value is attacker-controlled by construction (any order placer can set `order.user` to a malicious contract), and reaching `withdraw()` for that beneficiary only requires a normal `cancelOrder`/fill/refund flow completing — no privileged role is needed to become the "malicious beneficiary." However, actually turning this into a double-spend requires a reentrant path back into a second `onAccept`/`onGetResponse` invocation for the same commitment before the first `_orders` decrement lands, which depends on the ISMP host's (`EvmHost`) internal message-dedup/ordering guarantees. I could not fully verify from `IntentGatewayV2.sol` alone whether `EvmHost` marks a request/response as delivered before or after calling into the app, so full end-to-end exploitability of the double-spend is not confirmed with the code reviewed in the available time — the CEI violation itself, though, is directly verifiable in the file cited above.

### Recommendation
Apply checks-effects-interactions ordering in `withdraw()`: decrement `_orders[body.commitment][token]` (and clear `TRANSACTION_FEES`) before performing the external `.call{value: amount}("")`/token transfer, and add a `nonReentrant` guard (or the equivalent) to `withdraw()`/`onAccept`/`onGetResponse` as defense in depth, in addition to considering a fixed-gas-stipend transfer for the native-ETH branch to limit what recipient code can execute.

### Proof of Concept
1. Attacker places an order with `order.user` set to a malicious contract address they control (this is the unprivileged action available to any user).
2. Order is cancelled/refunded (or filled) and the cross-chain flow eventually causes `onAccept`/`onGetResponse` on `IntentGatewayV2` to call `withdraw()` with `beneficiary = order.user`.
3. During `beneficiary.call{value: amount}("")` inside the token loop [5](#0-4) , attacker's fallback executes while `_orders[body.commitment][token]` still reflects the pre-withdrawal (non-decremented) balance.
4. If the host/relayer layer permits any reentrant re-delivery of a message referencing the same commitment before local bookkeeping is finalized, the attacker can trigger a second `withdraw()` execution against the still-inflated `_orders` entry, redeeming the same escrow twice.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L536-537)
```text
            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-744)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
}
```
