### Title
Reentrant fund release in Tron `IntentGatewayV2.withdraw` violates checks-effects-interactions - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron-chain variant of `IntentGatewayV2.withdraw` transfers escrowed native tokens/ERC20s to the `beneficiary` **before** decrementing the `_orders[commitment][token]` escrow accounting, and does the same for accumulated transaction fees. This is the exact anti-pattern described in the external report (external call before state update), and it directly contradicts the hardened implementation used by the primary EVM contracts (`IntentsBase.sol`), which decrement escrow before making the external transfer.

### Finding Description
`withdraw()` is invoked from `onAccept` (for `RedeemEscrow`/`RefundEscrow` messages delivered by the host) and from `onGetResponse` (for cancellation refunds), both restricted with `onlyHost`: [1](#0-0) [2](#0-1) 

Inside `withdraw`, for each escrowed token the contract performs the external transfer (a raw native-value `.call` or a low-level ERC20 `transfer` call) and only afterwards decrements the escrow balance: [3](#0-2) 

The same unsafe ordering is repeated for the accumulated transaction fee payout: [4](#0-3) 

The `beneficiary` field of the `WithdrawalRequest` is attacker-influenced: for a `RedeemEscrow` message it is set to the solver's own address (`msg.sender` at `fillOrder` time on the destination chain), so an attacker acting as solver can set `beneficiary` to a malicious contract: [5](#0-4) 

This contrasts with the primary/hardened implementation in `IntentsBase.sol` (used by the standard EVM `IntentGatewayV2.sol`), which correctly decrements escrow **before** transferring funds out (checks-effects-interactions): [6](#0-5) 

### Impact Explanation
Because escrow accounting is only updated after the value transfer, a malicious `beneficiary` contract receiving native token can execute arbitrary code in its `receive`/`fallback` mid-transfer, while `_orders[commitment][token]` (and, for fees, `_orders[commitment][TRANSACTION_FEES]`) still reflect the pre-payout balance. This is a state-inconsistency window classic of reentrancy bugs, and any function reachable from that callback that reads or acts on the stale, not-yet-decremented escrow balance for the same commitment can be tricked into releasing funds that have already been (or are being) paid out, leading to loss of escrowed collateral/fees beyond what was legitimately owed. This is a fund-safety violation in the token-bridge/intents settlement path (theft of escrowed funds), matching the Medium/High severity class targeted by this scan.

### Likelihood Explanation
The vulnerable code path is reached whenever a relayer delivers a legitimately-proven `RedeemEscrow`/`RefundEscrow` message (or an `onGetResponse` for cancellation) — a routine, permissionless part of the intent-fill lifecycle. The `beneficiary` address is controlled by whichever party fills/cancels the order (the solver or the order owner), so no special privilege is required to set it to an attacker-controlled contract. The only extra requirement is a native-token order (to get a direct `.call` invoking `receive()`), which is a normal, supported configuration (`token == address(0)` branch exists explicitly in the code).

### Recommendation
Apply checks-effects-interactions consistently in the Tron `withdraw()` function, mirroring `IntentsBase._withdraw`: decrement `_orders[body.commitment][token]` (and delete the fee entry) **before** performing the native-value call or ERC20 transfer to `beneficiary`. Additionally, consider using `SafeERC20.safeTransfer` instead of raw low-level `.call` with manual success checks, and add a reentrancy guard on `onAccept`/`onGetResponse` as defense-in-depth.

### Proof of Concept
1. Attacker deploys a malicious contract `Evil` with a `receive()` fallback.
2. Attacker (as solver) calls `fillOrder` on the destination chain for a native-token order, setting the beneficiary bytes to `Evil`'s address (this is the solver's own `msg.sender`, so it is fully attacker-controlled), and the fill dispatches a `RedeemEscrow` message back to the source chain.
3. On the source chain, once the relayer delivers the proven message, `EvmHost.dispatchIncoming` → `IntentGatewayV2.onAccept` → `withdraw(body, false)` executes.
4. Inside `withdraw`, `beneficiary.call{value: amount}("")` invokes `Evil.receive()` **before** `_orders[body.commitment][address(0)] -= amount` executes.
5. Because state has not been updated yet, `Evil`'s fallback can attempt to trigger further logic dependent on the stale (pre-decrement) `_orders[commitment][address(0)]` balance (e.g., via any other reachable path that reads this mapping for the same commitment before the first call frame returns and applies its decrement), enabling a double-release of the same escrowed funds beyond the intended single payout. [7](#0-6)

### Citations

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
