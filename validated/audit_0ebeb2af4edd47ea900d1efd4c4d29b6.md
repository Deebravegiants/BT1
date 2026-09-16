### Title
Solver selection signature does not bind fill amounts, allowing selected solvers to deliver only the required minimum instead of their winning bid — ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
The `SolverSelection` EIP-712 message that a user signs with the order's session key authorizes a solver **address** for an order **commitment**, but never commits to the output amounts the solver actually quoted in its bid. `fillOrder()` then accepts an independently-supplied `FillOptions.outputs` parameter and only checks that it meets the order's bare minimum, not that it matches the amount the user selected the solver for. This is the same root cause as the referenced Gitcoin `RFPSimpleStrategy` finding: a value reviewed/approved at selection time (`proposalBid` there, the bid's `options.outputs` here) is not fixed by the approval, and can be freely substituted with a different, less favorable value at execution time.

### Finding Description
In `IntentsBase.sol::_select`, the signed struct is:
```solidity
bytes32 structHash = keccak256(abi.encode(SELECT_SOLVER_TYPEHASH, options.commitment, options.solver));
``` [1](#0-0) 

Only `(commitment, solver)` are bound; the transient-storage value stored for authorization is `keccak256(abi.encode(options.solver, sessionKey))` — again independent of any fill amount.

`IntentGatewayV2::fillOrder` then re-derives the same hash purely from `msg.sender` and `order.session`:
```solidity
bytes32 expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session));
if (storedSelectionHash != expectedSelectionHash) revert Unauthorized();
``` [2](#0-1) 

`options.outputs` (the actual amounts delivered) is a completely separate calldata parameter that is never checked against anything the user signed. The only constraint on it is enforced later, per-leg, inside the fill logic, and it is a **floor**, not an equality check:
```solidity
uint256 fillAmount;
...
} else {
    fillAmount = solverAmount > remaining ? remaining : solverAmount;
}
```
and cross-chain reverts only if `solverAmount < totalRequired` (`InvalidInput()`), per the documented flow. [3](#0-2) 

Because the off-chain auction (bids shown to the user via the coprocessor / `BIDS_RECEIVED` events) is what actually communicates a solver's promised `options.outputs`, and the on-chain authorization the user signs strips that information out, a solver can:
1. Submit an attractive bid (high `options.outputs`, i.e., generous surplus) to win the auction and get the user's `SolverSelection` signature over `(commitment, solver)`.
2. Call `select()` themselves with that same signature, then call `fillOrder()` with a **different** `FillOptions.outputs` — as low as `order.output.assets[i].amount` (the bare required minimum) — since nothing ties the authorization to the bid that was actually selected.

The result is a bait-and-switch: the user selects a solver based on a specific promised output amount, but the protocol only enforces solver identity, not delivered value, at settlement — exactly mirroring the `RFPSimpleStrategy` pattern where `recipient.proposalBid` could be swapped between milestone approval and `_distribute()`.

### Impact Explanation
This directly undermines the intent auction's economic guarantee: any surplus value a user was promised by selecting a particular winning bid can be withheld by the solver post-authorization, with the protocol enforcing only the order's minimum required output. Because `select`/`fillOrder` are plain external functions (not gated to only be called via the atomic `SolverAccount` UserOperation path — a solver can call `select()` and `fillOrder()` directly as shown in the gateway's own tests), a solver who has captured a valid session signature is free to deliver the minimum instead of what won the auction, extracting the difference for itself at the order placer's expense. This is a concrete loss-of-funds condition for users relying on the intent gateway's bid mechanism.

### Likelihood Explanation
Any solver that is legitimately selected already possesses the session signature (it must append it to its own UserOperation, or, when calling `select`/`fillOrder` directly as demonstrated in `IntentGatewayV2Test.sol`, it simply reuses the signature it received). No cryptographic or state binding prevents that same solver from substituting a smaller `FillOptions.outputs` at call time, so exploitation requires no special privilege beyond being the (honestly) selected solver — it is a rational, low-effort strategy for any solver to under-deliver relative to its winning quote.

### Recommendation
Bind the `SolverSelection` signature (and/or the transient-storage authorization) to the specific fill terms the user approved, e.g., include a hash of `FillOptions.outputs` (and any other economically relevant fields such as `relayerFee`) in the `SELECT_SOLVER_TYPEHASH` struct, and have `fillOrder` verify that the caller's `options` matches the hash committed to at `select()` time. Alternatively, require that `select()` be called with the exact `options` struct and store `keccak256(abi.encode(msg.sender, order.session, options))`, then have `fillOrder` re-derive and check against that value instead of only `(msg.sender, order.session)`.

### Proof of Concept
1. User places an order with `session` key S and solver-selection enabled.
2. Solver A submits a bid with `options.outputs = [2000 DAI]` (well above the 1000 DAI minimum), winning the auction.
3. User signs `SolverSelection{commitment, solver: A}` with session key S, authorizing A.
4. Solver A calls `IntentGatewayV2.select(SelectOptions{commitment, solver: A, signature})` directly, staging `tstore(commitment, keccak256(abi.encode(A, S)))`.
5. Solver A calls `fillOrder(order, FillOptions{outputs: [1000 DAI]})` — the bare minimum — instead of the 2000 DAI it bid. The `expectedSelectionHash` check in `fillOrder` still passes because it only checks `(msg.sender, order.session)`, and `_fillSameChain`/`_fillCrossChain` accept it because `1000 >= totalRequired`.
6. The user receives only the minimum output, while Solver A pockets the difference it never had to deliver, despite having won the auction on the promise of 2000 DAI.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L560-572)
```text
    function _select(SelectOptions calldata options) internal returns (address) {
        bytes32 structHash = keccak256(abi.encode(SELECT_SOLVER_TYPEHASH, options.commitment, options.solver));
        bytes32 digest = _hashTypedDataV4(structHash);
        address sessionKey = ECDSA.recover(digest, options.signature);

        bytes32 commitment = options.commitment;
        bytes32 selectionHash = keccak256(abi.encode(options.solver, sessionKey));
        assembly {
            tstore(commitment, selectionHash)
        }

        return sessionKey;
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L464-472)
```text
        if (_params.solverSelection) {
            bytes32 storedSelectionHash;
            assembly {
                storedSelectionHash := tload(commitment)
            }

            bytes32 expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session));
            if (storedSelectionHash != expectedSelectionHash) revert Unauthorized();
        }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L79-89)
```text
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
```
