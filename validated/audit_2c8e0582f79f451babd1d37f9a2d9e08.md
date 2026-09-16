### Title
Missing reentrancy protection and CEI violation in Tron `IntentGatewayV2.withdraw` allows escrow double-spend via malicious token callback - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron port of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) omits the reentrancy guard that protects the canonical EVM implementation, and its `withdraw()` function performs the external token transfer *before* decrementing the `_orders` escrow accounting mapping. This is the exact bug class from the external report: pull/push token flows combined with a callback surface that lets an attacker re-enter and drain escrowed funds before state is finalized.

### Finding Description
The EVM `IntentGatewayV2` (`evm/src/apps/IntentGatewayV2.sol:60`) explicitly inherits `ReentrancyGuardTransient` and guards `placeOrder` with `nonReentrant` [1](#0-0) , and the fill/withdraw internal logic (`IntentsBase._withdraw`, `IntrinsicIntents`/`ExtrinsicIntents`) sets `_filled[commitment]` at the top of fill functions specifically to defeat reentrancy, as confirmed by the dedicated regression suite `IntrinsicIntentsReentrancyTest.sol` [2](#0-1) .

The Tron variant of the same contract, however, declares `contract IntentGatewayV2 is HyperApp, EIP712` with no `ReentrancyGuard`/`ReentrancyGuardTransient` inheritance and no `nonReentrant` modifier anywhere in the file (confirmed by search — zero matches for `nonReentrant`/`ReentrancyGuard` in `evm/tron/contracts/**`) [3](#0-2) .

Its `withdraw()` function performs the external token transfer via low-level `.call` **before** decrementing the escrow balance:
```
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    ...
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    ...
}
_orders[body.commitment][token] -= amount;
``` [4](#0-3) 

Because the escrow decrement happens after the token `.call`, any token contract used as an order's input asset that executes attacker-controlled code during `transfer` (e.g., an ERC-777-style hook, a fee-on-transfer token with a callback, or any token whose `transfer` invokes an external contract) can re-enter the gateway while `_orders[commitment][token]` still reflects the pre-withdrawal balance. Unprivileged, user-reachable entry points that consult this same mapping — `_cancelSameChain`-equivalent same-chain cancellation and `placeOrder`'s escrow bookkeeping — can then be invoked again against the stale (not-yet-decremented) escrow value, enabling a double release of the same escrowed input token. This mirrors the reported Exchange bug class precisely: a pull/push funds flow whose external call precedes an internal accounting update, giving the "owner"/callback path (here, the malicious token contract acting during a fill/redeem sequence a user or solver initiates) the ability to trigger another privileged-looking function (`withdraw`, reachable via the escrow lifecycle) that drains user funds a second time.

### Impact Explanation
A successful reentrant call lets an attacker who controls (or has crafted) the input token contract for their own order withdraw/refund the same escrowed balance more than once, directly stealing funds from the gateway that back other users' escrowed orders — concrete theft of user funds, matching the "Medium/High/Critical" bar (unbacked release of escrow, permanent freezing/loss of other users' funds once the gateway's token balance is drained below what it owes).

### Likelihood Explanation
Reachable from a single unprivileged transaction: any user can call `placeOrder` with an attacker-controlled/malicious ERC-20 as an input token, and the relayed `withdraw()` path (via `onAccept`/`onGetResponse`, ultimately reachable through the normal fill/cancel/redeem lifecycle) executes the vulnerable `.call`-before-decrement sequence with no reentrancy guard anywhere in the contract. The likelihood is elevated by the fact that the sibling EVM contract needed an explicit CEI fix and a `ReentrancyGuardTransient` guard for the same code paths — the Tron port simply never received that fix.

### Recommendation
Add a reentrancy guard (`ReentrancyGuard`/`ReentrancyGuardTransient`) to the Tron `IntentGatewayV2` contract and apply it to all external entry points that move funds (`placeOrder`, `fillOrder`, `cancelOrder`, `onAccept`, `onGetResponse`). Additionally, fix `withdraw()` to follow checks-effects-interactions: decrement `_orders[body.commitment][token]` (and delete/adjust `TRANSACTION_FEES`) *before* performing the external `.call`/transfer, matching the pattern already used in the EVM `IntentsBase._withdraw`.

### Proof of Concept
1. Attacker deploys a malicious ERC-20 `EvilToken` whose `transfer()` function, when invoked by the gateway, re-enters `IntentGatewayV2` (e.g., calls `cancelOrder` for the same commitment, or triggers a second incoming request that reaches `withdraw` for the same commitment/token) before returning.
2. Attacker places a same-chain order via `placeOrder` using `EvilToken` as the escrowed input, receiving a valid `commitment`.
3. When settlement occurs and `withdraw(body, isRefund)` is invoked (via `onAccept`/`onGetResponse` in the normal redeem/refund flow), the `token.call(...transfer...)` at `evm/tron/contracts/apps/IntentGatewayV2.sol:706` triggers `EvilToken`'s callback.
4. Inside the callback, `_orders[commitment][token]` still holds its pre-withdrawal value (the decrement at line 710 has not executed yet), so the attacker's reentrant call can trigger another withdrawal/refund path that reads the stale balance and transfers out escrowed value a second time — effectively minting a second payout from the same escrow entry and draining the gateway's pooled token balance backing other users' orders.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L60-60)
```text
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-49)
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
 */
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
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
