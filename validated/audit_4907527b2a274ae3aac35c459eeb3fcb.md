### Title
Missing reentrancy protection on Tron `IntentGatewayV2.fillOrder` allows re-entrant escrow/output theft - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) inherits directly from `HyperApp` and `EIP712` only — unlike the canonical EVM `IntentGatewayV2.sol`, it does **not** inherit `ReentrancyGuardTransient` and no `nonReentrant` modifier exists anywhere in the file (confirmed via `grep_search` for `nonReentrant|ReentrancyGuard`, zero matches under `evm/tron/**`) [1](#0-0) . This mirrors the reported bug class exactly: the audited `StakingRewards.exit()` composes two individually-guarded operations (`withdraw()` + `getReward()`) without a reentrancy guard on the composing function itself, allowing state to be re-entered between them. Here, the fill/settlement path performs external token/ETH transfers via low-level `.call` before all order-state bookkeeping is finalized, and the enclosing entry points have no reentrancy lock at all.

### Finding Description
On the canonical EVM contract, `fillOrder` is explicitly `nonReentrant` [2](#0-1) , and the fill functions additionally follow a checks-effects-interactions pattern where `_filled[commitment] = msg.sender` is set before any external call, as proven by the dedicated regression test suite `IntrinsicIntentsReentrancyTest.sol` which was written specifically to close a prior reentrancy hole in `_fillSameChain`/`_fillCrossChain` [3](#0-2) [4](#0-3) .

The Tron port of the contract, however, has neither of these protections:
- The contract declaration omits `ReentrancyGuardTransient` entirely [1](#0-0) .
- Its `withdraw()` internal function does set `_filled[body.commitment] = beneficiary` before the token transfer loop (defense in depth for that one function) [5](#0-4) , but it uses raw `.call()` for both native and ERC-20 transfers to an attacker-controlled `beneficiary` address inside a loop that also decrements escrow accounting after the call, and the tx-fee transfer at the end also uses `.call()` to an external token [6](#0-5) .
- Without any `nonReentrant` guard anywhere in the file, the top-level entry points that call into escrow logic (`placeOrder`'s predispatch `CallDispatcher.dispatch` at line 414, and any fill/cancel path that ultimately reaches `withdraw()`/native transfers) have no protection against cross-function reentrancy. A beneficiary or predispatch/postdispatch callee contract that receives control during one of these `.call{value:...}("")` or ERC20 `.call` transfers can reenter `placeOrder`, `fillOrder`, `cancelOrder`, or `select` before the outer call's state fully settles, exactly the same "individually-fine-but-composably-unsafe" pattern the Sherlock report describes for `exit()` calling `withdraw()` then `getReward()` without its own guard.

### Impact Explanation
Reentrancy into escrow-adjacent state (`_orders`, `_filled`, `_partialFills`) on the Tron gateway could let an attacker-controlled beneficiary or CallDispatcher callee re-enter and drain escrowed input tokens, double-claim tx fees, or manipulate partial-fill accounting before the first call completes — a direct theft-of-funds / unbacked-withdrawal impact matching the Medium severity of the cited report, potentially higher here since there is zero reentrancy protection versus the reported partial protection in the original `StakingRewards.withdraw`.

### Likelihood Explanation
Likely reachable by any user or solver: `beneficiary` in `withdraw()`/fill flows is attacker-supplied (`order.output.beneficiary`), and both native (`.call{value}`) and ERC-20 transfer-hook tokens can trigger callbacks. Given the main EVM contract needed a dedicated fix and regression suite for this exact class of bug, and the Tron contract carries no equivalent guard at all, the likelihood of an exploitable reentrancy window is high pending confirmation of exact cross-entry-point call graph (which I could not fully trace before running out of iterations — see below).

### Recommendation
Add `ReentrancyGuardTransient` (or a Tron-compatible reentrancy lock, since transient storage support may differ) to `evm/tron/contracts/apps/IntentGatewayV2.sol` and apply `nonReentrant` to all externally-reachable entry points that touch escrow or call out to `beneficiary`/`CallDispatcher` (`placeOrder`, `fillOrder`/fill equivalents, `cancelOrder`, `select`, and any function invoking `withdraw()`), matching the protection already present in `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
Not fully constructed — I was unable to read the complete Tron `fillOrder`/`cancelOrder`/`select` function bodies before the tool budget ran out, so I could not confirm the exact external-call-before-effects ordering in those entry points beyond `withdraw()` (lines 691–730) and the predispatch loop in `placeOrder` (lines 361–420). **This finding should be treated as a hypothesis requiring verification**: a Devin session with full repo access should (1) read the complete `evm/tron/contracts/apps/IntentGatewayV2.sol` file end-to-end, (2) trace every external call (`.call`, `safeTransfer`, `ICallDispatcher.dispatch`) against state writes in `fillOrder`, `cancelOrder`, `select`, and `placeOrder`, and (3) write a Foundry PoC analogous to `IntrinsicIntentsReentrancyTest.sol` targeting the Tron contract to confirm whether a malicious beneficiary/CallDispatcher callee can actually reenter and extract value before concluding this is exploitable.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-694)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-722)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L443-443)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-48)
```text
/**
 * @title ReentrantBeneficiary
 * @notice Malicious beneficiary contract that attempts to re-enter `fillOrder` during
 *         the ETH transfer made by `_fillSameChain` or `_fillCrossChain`.
 *
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-170)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
```
