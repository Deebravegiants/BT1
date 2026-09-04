### Title
Unbound router input amount in `ExternalActionSwap`/`LifiExternalAction.callRouter` lets attacker sweep stray/residual input-token balance into their own output UTXO - ([File: contracts/external-actions/swaps/ExternalActionSwap.sol, contracts/external-actions/swaps/LifiExternalAction.sol])

### Summary
`ExternalActionSwap.swap` computes `swappedAmount` purely as a balance diff around an arbitrary `router.call(externalActionMetadata)`, and the ERC-20 branch of `LifiExternalAction.callRouter` grants the router `approveUnlimited` allowance without ever constraining the swap to `inputAmount` (the value Hinkal actually transferred in for that tx, `-deltaAmounts[0]`). Any input-token balance parked at the action contract beyond what Hinkal sent this transaction (e.g. an unspent-input refund from a prior partial-fill swap, or dust the attacker deposits directly) can be pulled into the attacker's swap call and converted 100% into the attacker's own shielded output UTXO.

### Finding Description
The invariant that should hold is: *tokens leaving the action contract in a transaction == `-deltaAmountChanges` that Hinkal transferred to it for that transaction*. Concretely, the input side should satisfy `router-consumed inputToken == inputAmount == uint256(-deltaAmounts[0])`.

Trace:
- `Hinkal._externalTransact` (`contracts/Hinkal.sol:244-256`) transfers exactly `uint256(-deltaAmountChanges[i])` of the input token to the external action, then calls `runAction`.
- `ExternalActionSwap.swap` (`contracts/external-actions/swaps/ExternalActionSwap.sol:40-68`) computes `inputAmount = uint256(-deltaAmounts[0])` (minus flat fee) and passes it to `callRouter`, but this value is **never used to bound the ERC-20 branch of the router call**.
- `LifiExternalAction.callRouter` (`contracts/external-actions/swaps/LifiExternalAction.sol:16-36`):
```solidity
approveUnlimited(inputToken, router);
(bool success, ) = router.call(externalActionMetadata);
require(success, "LI.FI swap failed: erc-20 token");
swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
```
`externalActionMetadata` is fully attacker-controlled calldata to the router; the router pulls whatever amount that calldata specifies via `transferFrom`, up to the unlimited allowance and the contract's actual token balance — not up to `inputAmount`. Only the native-coin branch (`msg.value: inputAmount`) is actually bounded.
- `swappedAmount` is then entirely handed to the caller: `transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal)` and packaged into `utxoSet[0]` (`ExternalActionSwap.sol:93-101`), which the attacker returns as their own freshly-proved UTXO.
- Back in `Hinkal.sol`'s post-action balance check (`contracts/Hinkal.sol:98-146`), the equation `balanceDif == amountChanges[i] + utxoAmount` is satisfied because `utxoAmount` is taken from the attacker's own returned UTXO and `amountChanges[i]` is a value the attacker freely chooses as part of their own proof; the circuit's `inTotal + amountChanges[i] === outTotal` (`circuits/MainEVMCircuit.circom:168`) only enforces internal self-consistency of the attacker's own witness, not that the swapped input amount matches what Hinkal actually sent this transaction. None of `performHinkalChecks`, `verifyProof`, `insertNullifiers`, or the slippage checks constrain how much of the input token the router is allowed to consume.

Exploit flow for an unprivileged attacker:
1. Cause (or find) a stray/residual input-token balance at the `LifiExternalAction` contract — either by waiting for a prior user's partial-fill swap to leave an unspent-input refund there, or simply by transferring tokens directly to the contract themselves (any EOA can do this).
2. Call `Hinkal.transact` with a small legitimate deposit (`deltaAmounts[0]` corresponding to a modest real transfer), and self-crafted `externalActionMetadata` that instructs the router to swap `inputAmount + residual` of the input token (the router will happily pull it since `approveUnlimited` was granted).
3. `swappedAmount` now reflects the larger swap; the attacker sets their own proof's output UTXO amount to match `amountToSendToHinkal`, creating a valid, fully self-consistent shielded UTXO that includes the stolen residual, with no nullifier ever spent to back the extra value.

### Impact Explanation
Direct theft of funds parked at (or self-seeded into) the external action contract, converted into a legitimately provable shielded UTXO under the attacker's control, with no proof/nullifier/root check catching the discrepancy. This matches Critical: "direct theft of shielded or in-flight user funds," since any residual belonging to the protocol/other users at the action contract can be swept by any unprivileged party, repeatably, each time residual/dust exists (or is seeded by the attacker themselves via a trivial ERC-20 transfer).

### Likelihood Explanation
Feasibility is high: no privileged role or router bug is required — LI.FI/diamond-style routers pull tokens strictly according to the amount encoded in the calldata the caller supplies, which is exactly `externalActionMetadata`, fully attacker-controlled. The attacker can self-seed the "residual" with an ordinary ERC-20 transfer to the action contract, making the precondition trivially attacker-controlled rather than dependent on chance. Cost is limited to the amount actually deposited via Hinkal plus gas; the reward is the full seeded/residual amount converted through the router.

### Recommendation
In `LifiExternalAction.callRouter` (and any other `ExternalActionSwap` router integration), bind the actual token pulled by the router to `inputAmount`:
- Record `inputTokenBalanceBefore` and `inputTokenBalanceAfter` around the router call and `require(inputTokenBalanceBefore - inputTokenBalanceAfter <= inputAmount)`, or
- Approve the router for exactly `inputAmount` (not unlimited) before each call and reset/verify the allowance afterward, so the router cannot pull more than what Hinkal sent for that transaction.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `LifiExternalAction`, a mock ERC-20, and a mock router that on `call` pulls an attacker-specified `pullAmount` via `transferFrom` and sends back a proportional `outputToken` amount.
2. Seed residual: from an arbitrary EOA, `token.transfer(lifiActionAddress, residualAmount)` directly (simulating a stray/refunded balance).
3. Attacker builds a valid `CircomData`/proof for a swap with `deltaAmounts[0] = -depositAmount` (small), and `externalActionMetadata` encoding `pullAmount = depositAmount + residualAmount`.
4. Call `Hinkal.transact(...)`.
5. Assert: `swappedAmount` (and therefore the attacker's created UTXO amount / balance received) reflects `depositAmount + residualAmount` worth of output, i.e., tokens leaving the action in the tx `>` `-deltaAmountChanges` Hinkal sent it that tx — violating the stated invariant — while `token.balanceOf(lifiActionAddress)` for the input token drops by `depositAmount + residualAmount`, confirming the residual was swept into the attacker's own output.