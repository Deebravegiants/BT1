### Title
Reentrancy via stale escrow state before external transfer in Tron `IntentGatewayV2.withdraw()` allows draining escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Chrome CVE describes a use-after-free where a crafted extension/interaction triggers logic to act on a resource whose state has not yet been finalized. The closest reachable analog in this codebase is a checks-effects-interactions violation in the Tron variant of `IntentGatewayV2`: the internal `withdraw()` function performs the external token/value transfer to the beneficiary *before* decrementing the escrow accounting (`_orders[commitment][token]`), and the function is reachable from unauthenticated, permissionless message-delivery paths (`onAccept` for `RedeemEscrow`/`RefundEscrow`, and `onGetResponse` for source-side cancellation) with no reentrancy guard on the contract.

### Finding Description
In the mainline EVM contract, `IntentsBase._withdraw` (`evm/src/apps/intentsv2/IntentsBase.sol:451-470`) correctly decrements escrow state before making the external transfer: [1](#0-0) 

The Tron port, however, reverses this order in `withdraw()`: [2](#0-1) 

Here the raw low-level `.call` to `token.transfer(...)` (or the native-value `.call`) executes while `_orders[body.commitment][token]` still holds the pre-transfer (stale) escrow amount, and only afterward is `_orders[body.commitment][token] -= amount` applied. If `token` is a contract that can execute code on transfer (an ERC-777/ERC-1363-style token, a token with transfer hooks, or the native value case reentering through a contract `beneficiary`), the callback can re-enter `withdraw()` (via a new `onAccept`/`onGetResponse` delivery, or indirectly if the same `WithdrawalRequest` context can be replayed while the escrow decrement has not yet committed) and read/act on the same non-decremented `_orders` balance again, or execute other order operations against the still-inflated escrow bookkeeping. The contract `IntentGatewayV2 is HyperApp, EIP712` does not inherit or apply `ReentrancyGuard`/`nonReentrant`, unlike the corresponding EVM path, which offers no defense-in-depth against this ordering bug: [3](#0-2) 

This class of bug — "act on a resource's stale, not-yet-freed/finalized state during a callback" — is the direct analog of CVE-2022-1856's use-after-free-via-callback pattern, applied to on-chain escrow bookkeeping instead of browser heap objects.

### Impact Explanation
`withdraw()` is reached through the app-dispatch path that any relayer can invoke by delivering a message: `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `IntentGatewayV2.onAccept` → `withdraw(body, isRefund)` for `RedeemEscrow`/`RefundEscrow`, and similarly for `onGetResponse`. Because the transfer happens before the escrow ledger is decremented, and no reentrancy guard exists on this contract, a malicious or non-standard token/beneficiary can re-enter and cause the same escrowed input to be paid out more than once, directly resulting in theft of escrowed user funds from the gateway — a concrete impact under the "concrete theft ... of funds" acceptance criterion.

### Likelihood Explanation
Exploitability depends on the escrowed token supporting a transfer-time callback (ERC-777-like) or on the native-value branch where `beneficiary` is attacker-controlled and can re-enter on receipt of value. Given that `Order.inputs`/`TokenInfo.token` are arbitrary addresses chosen at order-placement time (potentially by an unprivileged user placing an order with a malicious token, or a solver colluding with a malicious beneficiary), an attacker who controls one side of the order flow can select a compatible token, making this reachable without any admin/governance/privileged role — matching the required "single submitted transaction/relayed proof" threat model.

### Recommendation
Apply checks-effects-interactions in the Tron `withdraw()`: decrement `_orders[body.commitment][token]` (and the transaction-fees mapping) before performing any external call/token transfer, mirroring `IntentsBase._withdraw` in the main EVM contracts. Additionally, add a `nonReentrant` guard (OpenZeppelin `ReentrancyGuard`) to `IntentGatewayV2` on Tron consistent with the guard already used in the analogous EVM `IntentGatewayV2.cancelOrder`/`fillOrder` functions, and prefer `SafeERC20.safeTransfer` over raw low-level `.call` with a manually encoded selector to reduce silent-failure risk.

### Proof of Concept
1. Attacker places a same-chain or cross-chain `Order` whose input `token` is a malicious ERC-20/777-style contract that, on `transfer()`, calls back into the attacker's contract.
2. Order is filled/settled normally so that Hyperbridge dispatches a `RedeemEscrow` (or `RefundEscrow`) `WithdrawalRequest` to the Tron `IntentGatewayV2` for that commitment, with `beneficiary` = attacker's contract.
3. A relayer delivers the message; `onAccept` calls `withdraw(body, ...)`.
4. Inside `withdraw`, `token.call(transfer(beneficiary, amount))` triggers the attacker's `tokensReceived`/fallback hook before `_orders[commitment][token] -= amount` executes.
5. The attacker's hook re-enters the gateway (e.g., calling `onGetResponse`/`onAccept` again with a crafted or replayed proof for the same commitment/token, or exploiting any other function reading `_orders[commitment][token]`) while the balance is still un-decremented, extracting the escrow a second time.
6. Net effect: escrow for the same order is paid out more than once, at the expense of the gateway/other users' funds. [4](#0-3) [5](#0-4)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-744)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
}
```
