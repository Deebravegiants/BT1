### Title
Checks-Effects-Interactions Violation in `IntentGatewayV2.withdraw()` Enables Reentrancy During Escrow Release - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.withdraw()` performs external calls (native ETH transfer or ERC-20 `transfer` via low-level `.call`) to an attacker-influenced `beneficiary` address for each escrowed token **before** decrementing the corresponding `_orders[commitment][token]` accounting entry, and likewise transfers accumulated transaction fees before deleting the `TRANSACTION_FEES` entry. This is the same class of Checks-Effects-Interactions violation flagged in the external report's `_refund()` example (external transfer performed before internal state is updated).

### Finding Description
`withdraw()` is reached from `onAccept()` (called by the host on `RequestKind.RedeemEscrow` / `RequestKind.RefundEscrow` messages) and from `onGetResponse()` — both are triggered by relayed, ISMP-proof-verified cross-chain messages, i.e. attacker-influenceable inputs from a single relayed message/order fill. [1](#0-0) 

Inside `withdraw()`, for each token in the withdrawal request the function checks only that the escrow slot is non-zero, then makes the external transfer, and only afterward decrements the escrow: [2](#0-1) 

The same ordering issue repeats for the transaction-fee payout: the external transfer happens before `delete _orders[body.commitment][TRANSACTION_FEES];`: [3](#0-2) 

While `_filled[body.commitment] = beneficiary;` is set at the very top of `withdraw()` (mitigating the specific double-fill reentrancy pattern documented in `IntrinsicIntentsReentrancyTest.sol` for the mainline EVM contract), that guard only protects the `_filled` mapping — it does not protect the per-token `_orders[commitment][token]` balances, which remain unmodified (i.e., still reflect the pre-withdrawal escrowed amount) for every token in the loop that has not yet been processed, and for the `TRANSACTION_FEES` slot, at the moment the external call executes. A beneficiary that is a smart contract (a normal, expected case since intent solvers are frequently contracts) receives control during the native-ETH `.call{value: amount}("")`, or a token with hooks (e.g., ERC-777-style or callback-enabled tokens) can execute logic during `token.call(...transfer...)`, while these downstream, not-yet-decremented escrow slots for the same commitment are still readable/actionable by any other reachable path that consults `_orders[commitment][...]`.

This directly mirrors the reported anti-pattern: state (`_orders` mapping) is mutated only *after* the external interaction, rather than before, violating Checks-Effects-Interactions.

### Impact Explanation
Violating CEI at a fund-transfer site is a High severity structural weakness for an escrow contract holding real user/solver funds: any future code change, added token support (fee-on-transfer, rebasing, or callback tokens), or unnoticed reachable function that reads `_orders[commitment][token]` mid-loop turns this into a concrete double-spend/drain of the escrow, since the balance the reentrant call observes is the pre-payout balance, not the post-payout balance. Because withdrawal beneficiaries are external, uncontrolled addresses (order users/solvers), this is directly reachable by an unprivileged actor who places or fills an order and designates a malicious contract as beneficiary/solver.

### Likelihood Explanation
Likelihood is elevated because: (1) `withdraw()` is reached via the standard order-fill/cancel flow with no additional privilege needed beyond being a solver or order owner, both untrusted roles by design, (2) beneficiaries are frequently expected to be smart contracts (solvers), and (3) the loop processes multiple tokens/fees per call, so any additional token support or code path added later that reads the same `_orders` mapping during the callback window would be immediately exploitable without further changes to `withdraw()` itself.

### Recommendation
Refactor `withdraw()` to follow Checks-Effects-Interactions strictly: decrement `_orders[body.commitment][token]` (and `delete` the `TRANSACTION_FEES` slot) *before* making the external `.call`/`safeTransfer`, mirroring the fix already applied to `_fillSameChain`/`_fillCrossChain` for the `_filled` mapping. Consider also adding a reentrancy guard on `withdraw()`/`onAccept()`/`onGetResponse()` as defense-in-depth, and replacing raw `.call` with `SafeERC20.safeTransfer` consistently (as already done in the non-Tron `IntentsBase.sol._withdraw`, which correctly decrements before transferring).

### Proof of Concept
1. Solver places itself (a malicious contract `Evil`) as the fill beneficiary for a cross-chain order with two escrowed input tokens: token A (native ETH) and token B (ERC-20).
2. Solver fills the order on the destination chain; the source-chain settlement path eventually calls `IntentGatewayV2.onAccept` → `withdraw(body, false)` on the source chain, with `body.beneficiary = Evil`.
3. In the `withdraw` loop, iteration `i=0` processes token A: `_orders[commitment][A]` check passes, `Evil.call{value: amount}("")` executes — `Evil`'s `receive()` fires while `_orders[commitment][A]` is still un-decremented and `_orders[commitment][B]` is fully intact.
4. During this callback window, `Evil` can invoke any other externally reachable function in the same contract that consults `_orders[commitment][...]` for this same commitment (e.g. a cancellation or dust-sweep style path), observing stale (not-yet-reduced) escrow balances and potentially extracting value a second time before the original call finishes decrementing state.
5. Control returns to `withdraw`, which decrements `_orders[commitment][A]` only now — too late to prevent the reentrant read/action taken in step 4.

Note: the index limitations in this environment prevented tracing every downstream reachable function that consults `_orders[commitment][...]` (e.g., the Tron variant's `cancelOrder`/`selectSolver` internals) to fully confirm the exact double-spend call chain; a full audit/PoC in a Devin/Foundry session against this Tron contract is recommended to confirm the exact exploitable secondary entry point, but the root-cause CEI violation itself is confirmed directly in the code cited above.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L623-644)
```text
    /**
     * @notice Executes an incoming post request.
     * @dev This function is called when an incoming post request is accepted.
     * It is only accessible by the host.
     * @param incoming The incoming post request data.
     */
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
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
