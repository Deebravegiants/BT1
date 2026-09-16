## Title
Checks-Effects-Interactions violation in `IntentGatewayV2.withdraw()` allows double-spend of escrowed native-token orders via reentrancy - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

## Summary
The Tron variant of `IntentGatewayV2` performs external value transfers to a caller-controlled `beneficiary` address before updating the corresponding escrow accounting (`_orders[commitment][token]`), and unlike the mainline EVM contract, this Tron contract has no reentrancy guard at all.

## Finding Description
`withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` is invoked from `onAccept` (for `RedeemEscrow`/`RefundEscrow` requests) and from `onGetResponse`. It checks `_orders[body.commitment][token] == 0`, then sends native ETH/TRX or ERC20 tokens directly to `beneficiary` via a low-level `.call`, and only *afterward* decrements `_orders[body.commitment][token] -= amount`: [1](#0-0) 

The transaction-fee redemption at the end follows the same unsafe order — external `.call` to the fee token happens before `delete _orders[body.commitment][TRANSACTION_FEES]`: [2](#0-1) 

Because `beneficiary` is attacker-controlled (it comes from `body.beneficiary`, ultimately the order's `user`/solver address chosen by the order creator), a malicious contract can be set as beneficiary for a native-token (`token == address(0)`) escrow. When `withdraw()` calls `beneficiary.call{value: amount}("")`, control transfers to the attacker's contract *before* `_orders[commitment][token]` is decremented. The attacker's `receive()`/fallback can re-enter `onGetResponse` (or, for a same-chain path, another externally reachable entry point that eventually calls `withdraw` again) for the same `commitment`. Since the balance check `_orders[body.commitment][token] == 0` has not yet been updated, the reentrant call passes the check and pays out the same escrow a second time.

This is a direct structural analog of the reported bug class: an external call is made mid-function, before the state (`_orders` mapping / effects) is finalized, violating checks-effects-interactions. Critically, the mainline EVM contract (`evm/src/apps/IntentGatewayV2.sol`) mitigates this class of bug by inheriting `ReentrancyGuardTransient` and by writing `_filled[commitment]` at the very top of the fill functions (confirmed by the CEI-fix regression tests in `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`), but the Tron contract: [3](#0-2) 
declares only `HyperApp, EIP712` — no `ReentrancyGuardTransient` — and no `nonReentrant` modifier exists anywhere in the file, unlike the mainline version: [4](#0-3) [5](#0-4) 

While `_filled[body.commitment] = beneficiary` is set before the token loop in `withdraw()`, this write alone doesn't gate re-entry into `withdraw()` itself — nothing in `withdraw()` checks `_filled` before proceeding, so a reentrant call to `withdraw()` (via `onGetResponse`, reachable any time the host delivers a matching GET response, or via a second `RedeemEscrow`/`RefundEscrow` POST) will pass the per-token zero-check because the decrement hasn't happened yet.

## Impact Explanation
This permits theft/double-redemption of escrowed order funds (native token and, depending on ERC20 implementation with callback hooks such as ERC777-style tokens, the ERC20 path too) held by the Tron `IntentGatewayV2` — a direct loss of user/solver escrowed funds, which is the "concrete theft of funds" impact class explicitly in scope.

## Likelihood Explanation
Reachable from a single relayed GET response (`onGetResponse`) or a relayed POST redeem/refund message (`onAccept`) delivered by any relayer once the order beneficiary is a malicious contract that the order's owner/solver controls — no privileged role is required to trigger the withdrawal path, only that a native-token order exists with a beneficiary/solver address the attacker controls. This matches an "unprivileged... intent solver" actor explicitly listed as in-scope.

## Recommendation
Apply the same checks-effects-interactions fix already used by the mainline `evm/src/apps/IntentGatewayV2.sol`:
1. Add a reentrancy guard (e.g. `ReentrancyGuardTransient`) to the Tron `IntentGatewayV2` contract and mark `onAccept`/`onGetResponse`/`withdraw` (or its outer callers) `nonReentrant`.
2. In `withdraw()`, decrement `_orders[body.commitment][token] -= amount` (and delete the fee entry) *before* making the external `.call` transferring value/tokens to `beneficiary`.

## Proof of Concept
1. Attacker (as solver/beneficiary) creates or fills a cross-chain order with a native-token (`token == address(0)`) output and deploys a malicious `beneficiary` contract with a `receive()` that calls back into the gateway's GET-response path for the same commitment.
2. Relayer delivers the GET response; `onGetResponse` → `withdraw(body, true)` executes: `beneficiary.call{value: amount}("")` transfers funds and yields control to the attacker's `receive()` before `_orders[commitment][token] -= amount` runs.
3. The attacker's `receive()` triggers a second delivery/processing of the same `WithdrawalRequest`/commitment (e.g. by having a second relayer-submittable GET response or replay of the POST redeem message for the same commitment), which again passes `_orders[body.commitment][token] == 0` check (still non-zero) and pays out the escrow a second time.
4. Net effect: the attacker receives `2×amount` for a single escrowed order, draining the gateway's held funds.

Note: I could not fully trace every external call path that can re-enter `withdraw()` within the time available (e.g., whether `onAccept`'s `RedeemEscrow`/`RefundEscrow` path can be triggered a second time for the same commitment before the host's own request-receipt replay protection blocks it). The `onGetResponse` path has no such receipt-replay protection visible in this file, which is the primary confirmed reentrant path.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-55)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L24-24)
```text
import {ReentrancyGuardTransient} from "@openzeppelin/contracts/utils/ReentrancyGuardTransient.sol";
```

**File:** evm/src/apps/IntentGatewayV2.sol (L60-60)
```text
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
```
