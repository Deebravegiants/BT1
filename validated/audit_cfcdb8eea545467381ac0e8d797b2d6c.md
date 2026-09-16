### Title
Checks-Effects-Interactions violation in `IntentGatewayV2.withdraw` (Tron variant) — escrow accounting updated after external token transfer - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron fork of `IntentGatewayV2` still contains the pre-CEI-fix pattern that the mainline EVM contract has already patched: in `withdraw()` the contract performs the external asset transfer (native `.call{value}` or ERC-20 `token.call(transfer(...))`) to the beneficiary **before** decrementing the escrow accounting variable `_orders[commitment][token]`. This is the same bug class as the CreamFi `gulp()` report: an internal custody-accounting variable (`totalReserves`/`internalCash` there, `_orders[...]` here) is mutated only *after* an external call that can hand control to an attacker-controlled contract.

### Finding Description
`IntentGatewayV2.withdraw` (Tron variant) is called from `onAccept` (for `RedeemEscrow`/`RefundEscrow`) and from `onGetResponse`, both gated `onlyHost`, and is triggered by a relayer-submitted ISMP proof: [1](#0-0) 

The relevant loop body:
```
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;
```
The external transfer happens first; the escrow bookkeeping decrement happens second. Additionally, the pre-transfer guard only checks `_orders[commitment][token] == 0` (i.e., "some escrow exists"), not `amount <= _orders[commitment][token]` — the amount bound is enforced only implicitly by Solidity 0.8 checked-arithmetic underflow on the *subsequent* line.

By contrast, the mainline (already-fixed) EVM implementation in `IntentsBase._withdraw` performs the decrement first and the transfer second: [2](#0-1) 

This confirms the team explicitly adopted a CEI fix for the mainline EVM contracts (see also the dedicated regression suite `IntrinsicIntentsReentrancyTest.sol`), but the Tron contract copy was not updated to match. [3](#0-2) 

### Impact Explanation
`_orders[commitment][token]` is the source-of-truth escrow ledger backing real bridged funds for `IntentGatewayV2`. Any function that performs an external call (handing control to a beneficiary/attacker contract) while the escrow ledger for that commitment/token pair is still un-decremented creates a window in which reentrant logic could observe or act on stale accounting. Because the loop iterates over `body.tokens` for a single `WithdrawalRequest`, a beneficiary contract that receives a native-ETH (or malicious/callback-capable token) payout mid-loop gains control before the remaining tokens in the same request are decremented and before the fee-escrow at the end of the function is settled — an unsafe pattern for a contract holding pooled user/solver funds. This is a Medium/High-severity code-quality and safety defect in a fund-custody function reachable purely by delivering a relayed cross-chain message (no privileged role required to trigger the code path — any relayer can submit the proof that invokes `onAccept`/`onGetResponse`).

### Likelihood Explanation
Reachability is high (any relayer/message delivery invokes this path), but full exploitability to actually double-spend/drain funds is constrained in the current code by: (1) `_filled[commitment]` being set at the top of `withdraw()` before the loop, which blocks reentrant calls into `fillOrder`/`cancelOrder` for the *same* commitment, and (2) `EvmHost`-style replay protection recording the request receipt before invoking the app's `onAccept`, blocking re-triggering the same incoming request. These guards reduce the practical blast radius, but they do not make the ordering safe in general — any future code path, token with transfer hooks (e.g., ERC-777-like or fee-on-transfer/callback tokens), or additional public function that reads `_orders[commitment][*]` without checking `_filled` would reopen a real fund-drain vector. The missing "amount <= escrowed" explicit check (relying implicitly on revert-on-underflow) is also fragile and should be made explicit.

### Recommendation
Apply the same CEI fix used in `IntentsBase._withdraw` to the Tron `IntentGatewayV2.withdraw`: decrement `_orders[body.commitment][token]` (and the `TRANSACTION_FEES` entry) **before** performing the external transfer, and explicitly `require(amount <= _orders[commitment][token])` rather than relying on the incidental revert from unsigned-integer underflow. Add a reentrancy guard to `withdraw`/`onAccept`/`onGetResponse` as defense-in-depth, mirroring the `nonReentrant` protections already used elsewhere in the codebase (e.g. `cancelOrder`).

### Proof of Concept
Not independently reproducible from indexed content alone — a full PoC (deploying `IntentGatewayV2` Tron variant with a malicious ERC-20/native beneficiary similar to `ReentrantBeneficiary` in `IntrinsicIntentsReentrancyTest.sol`, and demonstrating a state-inconsistent read within the same `withdraw` call before the guards described above intervene) would need to be built and run in a Devin session with repo/tool access; this exceeds what can be confirmed via static code reading alone from the ask-only investigation.

### Citations

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
