## Analysis

The Sherlock report describes a Checks-Effects-Interactions violation in `YsDistributor.claimRewards`: state (`rewardsClaimedForToken`) is only updated *after* the external token transfer, opening a reentrancy window. The strongest structural analog in Hyperbridge is the Tron build of the Intent Gateway's escrow-release routine.

`evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw()` performs the native/ERC20 transfer to the attacker-influenced `beneficiary` **before** decrementing the `_orders[commitment][token]` escrow accounting, and unlike the canonical EVM build the Tron contract has **no `nonReentrant` guard anywhere** in the file, whereas `evm/src/apps/IntentGatewayV2.sol` uses `nonReentrant` on `cancelOrder` (9 occurrences across the contract) and its `_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` decrements escrow state before transferring. [1](#0-0) 

### Title
Reentrancy in Tron IntentGatewayV2's `withdraw()` due to escrow-decrement-after-external-call and missing reentrancy guard - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`withdraw()` (called from `onAccept` on `RedeemEscrow`/`RefundEscrow` and from `onGetResponse` on cancel-from-source) transfers escrowed tokens/native value to `beneficiary` via a raw low-level `.call` **before** updating `_orders[commitment][token]`, and the Tron `IntentGatewayV2` contract entirely lacks a reentrancy guard (`nonReentrant` appears zero times in `evm/tron/contracts/apps/IntentGatewayV2.sol`, versus nine occurrences in the canonical `evm/src/apps/IntentGatewayV2.sol`).

### Finding Description
In `withdraw()`:
```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;   // <-- state updated AFTER the external call
``` [2](#0-1) 

Since `beneficiary` is decoded from the message body (`address(uint160(uint256(body.beneficiary)))`) and is attacker-controlled when a solver or user sets the beneficiary of an order, a native-token release (`token == address(0)`) hands control to an arbitrary contract via `beneficiary.call{value: amount}("")` while `_orders[commitment][token]` still shows the pre-decrement (non-zero) balance. The same file has no `nonReentrant` modifier on any external entry point (`placeOrder`, `fillOrder`, `cancelOrder`, `onAccept`, `onGetResponse`), unlike the mainline EVM contract in `evm/src/apps/IntentGatewayV2.sol`, whose `cancelOrder` is `nonReentrant` and whose escrow-release helper in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw` decrements `_orders` *before* transferring. [3](#0-2) [4](#0-3) 

The Tron build is a divergent, unguarded implementation, so the CEI-violation is directly reachable and unmitigated there.

### Impact Explanation
A beneficiary contract that receives the native-token leg of `withdraw()` can, in its fallback/receive, re-enter the gateway while `_orders[commitment][token]` (and other escrow slots for the same commitment, or same-chain partial-fill paths) is still non-zero, or re-enter before the transaction-fee slot (`_orders[body.commitment][TRANSACTION_FEES]`) is deleted — potentially draining escrowed tokens/fees more than once for a single settled order. This is concrete theft of escrowed user/solver funds, matching the "concrete theft ... of funds" bar.

### Likelihood Explanation
`withdraw()` is reached on every cross-chain fill settlement (`RedeemEscrow`) and every cancellation (`RefundEscrow`, and the GET-response cancel-from-source path), each of which is a normal, permissionless part of the Intent Gateway flow — no privileged actor is required, only an order whose beneficiary is a malicious contract. Given the pattern is present and the contract carries zero reentrancy protection, exploitation only requires crafting a beneficiary contract with a malicious `receive()`.

### Recommendation
Apply Checks-Effects-Interactions in `withdraw()`: decrement `_orders[body.commitment][token]` (and delete the `TRANSACTION_FEES` slot) *before* performing the native/ERC20 transfer, mirroring `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`, and add a `nonReentrant` guard consistent with the canonical `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Attacker places/fills a cross-chain order (or acts as the destination-chain canceller) such that `WithdrawalRequest.beneficiary` resolves to an attacker-controlled contract `Evil`.
2. Hyperbridge delivers the settlement/refund message; `onAccept` → `withdraw(body, ...)` runs.
3. For the native-token leg, `beneficiary.call{value: amount}("")` invokes `Evil.receive()` before `_orders[commitment][token] -= amount` executes.
4. `Evil.receive()` re-enters a reachable path that reads/uses `_orders[commitment][token]` (still un-decremented) — e.g., triggering another settlement/cancel flow for the same commitment through a queued duplicate message or a parallel order path sharing escrow accounting — extracting more value than was actually escrowed before the first decrement lands. [5](#0-4)

### Citations

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L505-505)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
```
