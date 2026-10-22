# [H] Unable to redeem from Notional

## Summary
Severity: High
Contest weight: 0.1195
Dataset id: 11508
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the redemption workflow of the Notional protocol when accessed through the Redeemer.sol contract. The function named maxRedeem is declared as a view function and simply returns the caller's token balance by invoking balanceOf(owner). Because view functions are read‑only, no state‑changing operation is performed to actually transfer or burn the principal token (PT) that the user intends to redeem. The contract’s external interface expects maxRedeem to calculate the amount that can be withdrawn and then to trigger the redemption, but the implementation stops at returning the balance, leaving the PT untouched. This mismatch between the function’s name and its effect creates a logical flaw: users invoke the redemption flow, receive a seemingly valid amount from maxRedeem, yet no subsequent call is made to the Notional core contract that would execute the redemption. Consequently, the user’s PT remains locked in the Notional system, and from the user’s perspective the UI may show a successful redemption request while the actual token balance on the blockchain does not change, leading to symptoms such as “my balance stays the same,” “I received nothing after redeeming,” or “my funds disappeared.” The bug is discovered during a security audit that inspected the Redeemer.sol source and noticed that the maxRedeem function does not contain any calls to Notional’s redeem logic, nor does it emit events indicating a transfer. The issue can be hard to notice because the function returns a plausible number and does not revert, so callers may assume the redemption succeeded. The impact is high: token holders are unable to withdraw their PT, breaking the protocol’s promised liquidity and potentially causing loss of confidence. The problem occurs every time a user attempts to redeem PT through Redeemer.sol, regardless of the amount or user role, because the view function never triggers the required state transition. To remediate, the maxRedeem function should be redesigned as a non‑view function that invokes Notional’s redemption entry point, updates internal accounting, and transfers the redeemed PT back to the caller, or the contract should separate the calculation of the redeemable amount from the actual redemption call, ensuring that the latter is executed in a state‑changing transaction. In general, the bug belongs to the class of "missing state‑changing operation" or "incorrect function mutability" errors, where a function intended to perform an action is mistakenly marked as read‑only, resulting in expected side effects never occurring.

## Proof of Concept
Notional code:
    
function maxRedeem(address owner) public view override returns (uint256) {
    return balanceOf(owner);
}

## Recommendation
No recommendation
