### Title
Duplicate output tokens in a same-chain order cause `_fillSameChain` to underflow-revert, permanently blocking fills until deadline - (evm/src/apps/intentsv2/IntrinsicIntents.sol)

### Summary
`_fillSameChain` tracks partial-fill progress per `(commitment, outputToken)` in `_partialFills`, but iterates per output-asset *index*, not per unique token. If an order's `output.assets` array contains the same token in more than one leg (with different per-leg `amount`s), the second leg's `alreadyFilled` read reflects the first leg's fill progress for that token, not its own. This produces an unchecked-looking but Solidity-0.8-checked subtraction `totalRequired - alreadyFilled` that can underflow and revert the entire `fillOrder` transaction on the very first fill attempt — a rounding/accounting-style revert directly analogous to the WiseLending `_calculateShares`/`lendingPoolData` mismatch: an internal counter that is not correctly scoped to the value it is being compared against, causing an otherwise-legitimate solver action to revert.

### Finding Description
In `_fillSameChain` (`evm/src/apps/intentsv2/IntrinsicIntents.sol:65-119`), for each output leg `i`:

```solidity
bytes32 outputToken = order.output.assets[i].token;
...
uint256 totalRequired = order.output.assets[i].amount;
uint256 solverAmount = options.outputs[i].amount;

uint256 alreadyFilled = _partialFills[commitment][outputToken];
uint256 remaining = totalRequired - alreadyFilled;
``` [1](#0-0) 

`_partialFills` is keyed only by `(commitment, outputToken)` — not by leg index:
```solidity
mapping(bytes32 => mapping(bytes32 => uint256)) public _partialFills;
``` [2](#0-1) 

If `order.output.assets` contains the same token at two different indices (e.g., leg 0 requires 100 of token X, leg 1 requires 30 of token X — nothing in `placeOrder`/`fillOrder` rejects duplicate tokens across legs), then within a single `fillOrder` call:
1. Leg 0 is processed: `alreadyFilled = 0`, the solver fully fills 100, and `_partialFills[commitment][X]` is set to `100`.
2. Leg 1 is processed in the same loop: `alreadyFilled` is now read back as `100` (leftover from leg 0, same storage slot), while `totalRequired` for leg 1 is only `30`. The subtraction `totalRequired - alreadyFilled = 30 - 100` underflows and reverts under Solidity 0.8 checked arithmetic.

This is architecturally the same class of bug as the WiseLending report: an internal bookkeeping variable (`lendingPoolData[_poolToken].totalDepositShares` there, `_partialFills[commitment][outputToken]` here) diverges from the value it's compared against (`pseudoTotalPool`/`currentSharePriceMax` there, `totalRequired` per-leg here) because the two are updated/read at different granularities, producing a revert on an otherwise valid, single-transaction operation performed by an unprivileged actor (a solver calling `fillOrder`).

### Impact Explanation
Any solver attempting to fill such an order reverts unconditionally, on the very first fill attempt and every attempt thereafter, because `_partialFills[commitment][X]` is permanently pinned to the first leg's terminal fill amount inside `_fillSameChain`'s own loop and is never able to satisfy the second leg's smaller `totalRequired`. The order becomes unfillable by any solver until `order.deadline` passes and the user cancels via `cancelOrder`/`_cancelSameChain`. This freezes the user's escrowed input tokens for the duration of the order and denies solvers the ability to earn the intended fee, which matches the report's "denial of a legitimate protocol action via an accounting/rounding mismatch" bug class. Because the affected mapping is shared across the whole loop body executed in one transaction, the underflow is guaranteed rather than probabilistic (unlike the WiseLending case, which required specific rounding remainders) — so likelihood of hitting the failure is 100% for any order shaped this way.

### Likelihood Explanation
Likelihood depends on whether a user (or a buggy/adversarial order-placing UI/SDK) can construct an order whose `output.assets` includes the same token more than once with different amounts. Nothing in the `Order`/`fillOrder` path that was inspected (`IntrinsicIntents.sol`, `IntentsBase.sol`) rejects duplicate tokens in `output.assets`; validation of `Order` structure was not fully located within the available context (the on-chain `placeOrder`/order-validation entry point lives in `evm/src/apps/IntentGatewayV2.sol`, which could not be fully inspected before the tool budget was exhausted). This is a plausible but not exhaustively confirmed user-controllable order shape — flagged as the main uncertainty in this analog.

### Recommendation
Key `_partialFills` (and the `alreadyFilled`/`remaining` computation) by `(commitment, i)` — the output-asset index — rather than solely by `outputToken`, so that multiple legs sharing the same token are tracked independently. Alternatively, reject orders whose `output.assets` contains duplicate token entries at order-placement time.

### Proof of Concept
1. User places a same-chain order with `order.output.assets = [{token: X, amount: 100}, {token: X, amount: 30}]` (single beneficiary, two legs of the same token).
2. Solver calls `fillOrder` providing `options.outputs = [{token: X, amount: 100}, {token: X, amount: 30}]`.
3. In `_fillSameChain`'s loop, iteration `i=0` fully fills leg 0: `_partialFills[commitment][X]` is set to `100`.
4. Iteration `i=1`: `alreadyFilled = _partialFills[commitment][X] = 100`, `totalRequired = 30`; `remaining = totalRequired - alreadyFilled = 30 - 100` reverts with a Solidity arithmetic underflow panic.
5. The entire `fillOrder` transaction reverts; the order remains permanently unfillable until `order.deadline`, at which point only cancellation (`_cancelSameChain`) can release the escrow back to the user. [3](#0-2) [2](#0-1)

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L65-92)
```text
        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
            }

            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L153-157)
```text
    /**
     * @dev Maps (commitment, output token) to the cumulative amount already filled.
     * Used to track partial fill progress for same-chain orders.
     */
    mapping(bytes32 => mapping(bytes32 => uint256)) public _partialFills;
```
