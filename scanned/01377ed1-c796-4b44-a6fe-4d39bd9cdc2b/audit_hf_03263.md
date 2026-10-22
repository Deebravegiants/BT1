# [M] `_buyoutLien`

## Summary
Severity: Medium
Contest weight: 0.4542
Dataset id: 17905
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logic flaw in the internal function that processes a lien buyout. When a caller attempts to purchase a lien, the function iterates over the existing stack of liens, accumulates the total debt that would be owed (potentialDebt) and checks that this amount does not exceed the liquidationInitialAsk value associated with each lien. However, the comparison is performed against the liquidationInitialAsk stored in the original (old) stack that was supplied as input, not against the stack that will exist after the new lien is inserted (the newStack). Because the function later replaces part of the stack with a new lien, the liquidationInitialAsk of the affected position can change, but the validation step never sees the updated value. Consequently, a malicious actor can craft a buyout where the accumulated debt is higher than the true liquidationInitialAsk of the resulting stack, bypassing the intended safety check. The exploit proceeds by calling the buyout function with a stack that contains an expired or near‑expiry lien, causing the loop to compute a potentialDebt that exceeds the real liquidation threshold. Since the contract checks the old threshold, the transaction succeeds and the buyer acquires a lien that is under‑collateralised. When the protocol later attempts to liquidate the position, the bids collected may be insufficient to cover the outstanding debt, leading to a shortfall of funds. Users observing the UI may see that their expected refund or payout is zero or far lower than anticipated, while the protocol’s accounting shows a mismatch between debt and available collateral. The issue was discovered during a Code4rena audit, where reviewers noted a comment marking the use of the old stack as a potential bug. It is difficult to spot because the code appears to perform a sensible check, and typical test cases may not exercise the path where the new stack’s liquidationInitialAsk differs from the old one. The proper remediation is to perform the liquidationInitialAsk validation against the stack after the replacement (newStack) or to recompute the threshold based on the new lien’s details before finalising the buyout, ensuring that the debt never exceeds the actual liquidation ask. This class of bug falls under “state‑inconsistent validation” where a contract validates against stale state, breaking accounting invariants and allowing economic loss.

## Proof of Concept
_buyoutLien() will validate against liquidationInitialAsk, but incorrectly uses the old stack for validation

```solidity
function _buyoutLien(
  LienStorage storage s,
  ILienToken.LienActionBuyout calldata params
) internal returns (Stack[] memory newStack, Stack memory newLien) {

....

  uint256 potentialDebt = 0;
  for (uint256 i = params.encumber.stack.length; i > 0; ) {
    uint256 j = i - 1;
    // should not be able to purchase lien if any lien in the stack is expired (and will be liquidated)
    if (block.timestamp >= params.encumber.stack[j].point.end) {
      revert InvalidState(InvalidStates.EXPIRED_LIEN);
    }

    potentialDebt += _getOwed(
      params.encumber.stack[j],
      params.encumber.stack[j].point.end
    );

    if (
      potentialDebt >
      params.encumber.stack[j].lien.details.liquidationInitialAsk   //1.****@audit use old stack
    ) {
      revert InvalidState(InvalidStates.INITIAL_ASK_EXCEEDED);
    }

    unchecked {
      --i;
    }
  }  
....
  newStack = _replaceStackAtPositionWithNewLien(
    s,
    params.encumber.stack,
    params.position,
    newLien,
    params.encumber.stack[params.position].point.lienId    //2.****@audit replace newStack
  );
```

## Recommendation
Replace then verify, using the newStack[] for verification.
