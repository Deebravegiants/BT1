# [H] Redeemer.redeem

## Summary
Severity: High
Contest weight: 0.5375
Dataset id: 11419
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the redeem function of the Redeemer contract, which is responsible for moving external principal tokens (PT) from the lender component to the redeemer component after a user withdraws their Element position. Instead of sending the withdrawn PT to the Redeemer contract itself, the code forwards the tokens to a variable named marketPlace. This misdirection is a logical error in the accounting flow: the contract assumes that the marketplace address will correctly forward the tokens onward, but the marketplace does not have any logic to receive and re‑deposit the PT, resulting in the tokens becoming effectively locked or lost. The root cause is the incorrect argument passed to the IElementToken.withdrawPrincipal call; the second parameter, intended to be the destination address, is set to marketPlace rather than the address of the Redeemer contract (address(this)). An attacker or an honest user can trigger this bug simply by invoking the redeem function with any non‑zero amount, after which the contract attempts to transfer PT to the wrong address. Because the marketplace contract does not implement a matching deposit interface, the PT never reaches the intended holder, leading to a reduction of the user’s balance and a potential total loss of the withdrawn principal. The impact is severe: users expect that calling redeem will return their PT to their wallet or to a known contract, but instead the tokens disappear from the system, violating the fundamental business rule that every withdrawal must be reimbursed in full. The condition occurs each time Redeemer.redeem is executed for Element tokens, regardless of the amount, as long as the withdrawPrincipal call is reached. The affected parties are the end users who hold Element positions, the protocol that relies on accurate accounting of PT, and any third‑party services that display user balances. The issue was discovered during a formal security audit by Code4rena, where the auditors compared the intended flow described in the project’s README with the actual implementation and noted the mismatch. This type of bug can be hard to notice because the transaction may not revert; it appears successful on‑chain, yet the tokens are transferred to an address that does not expose them, making the loss silent. To remediate the problem, the withdrawPrincipal call should be amended so that the destination address is the Redeemer contract itself (address(this)), ensuring that the PT is correctly received and can be subsequently transferred to the rightful user. Conceptually, this fixes a misrouted fund transfer, aligning the contract’s behavior with the expected accounting invariant that withdrawn principal tokens are always returned to the caller’s control. From a user perspective, the current bug manifests as a missing or zero token balance after a redeem operation, contrary to the expectation that the user receives their tokens back. By correcting the address argument, the contract restores the guarantee that funds are not unintentionally lost during redemption.

## Proof of Concept
According to the ReadMe.md, Redeemer should transfer external principal tokens from Lender.sol to Redeemer.sol.

But it transfers to the “marketPlace” and it would lose the PT.

## Recommendation
Modify [IElementToken(principal).withdrawPrincipal(amount, marketPlace);](https://github.com/code-423n4/2022-06-illuminate/blob/92cbb0724e594ce025d6b6ed050d3548a38c264b/redeemer/Redeemer.sol#L187) like this.
```solidity
IElementToken(principal).withdrawPrincipal(amount, address(this));
```
