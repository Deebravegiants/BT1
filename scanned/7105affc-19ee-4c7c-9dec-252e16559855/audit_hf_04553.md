# [C] C-03 | spTKN Oracle Can Be Manipulated With Donation

## Summary
Severity: Critical
Contest weight: 0.2377
Dataset id: 22156
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The price of a spTKN is affected by the amount and price of the underlying token in the pod. This is accounted for in _accountForCBRInPrice which does: (_amtUnderlying * IERC20(_underlying).balanceOf(_pod) * 10 * IERC20Metadata(_pod).decimals()) / IERC20(_pod).totalSupply() / 10 * IERC20Metadata(_underlying).decimals(); The problem lies in using the balance of underlying the pod, which can be easily manipulated through a donation of the underlying token to the pod. This would increase the value of spTKN and subsequently the aspTKN, which is the collateral token in FraxPairLend. Although the attacker loses the donated tokens, they can manipulate the oracle pricing to borrow more tokens from the lending protocol, exploiting the system. Low liquidity pods are more susceptible to such attacks.

## Proof of Concept
https://github.com/GuardianAudits/peapods-1/pull/11/files#diff-bb01fe0744b00ee5295dc1ee77236cace57c18239d7220224f78c6464570bdb7

## Recommendation
Instead of using balanceOf, use a storage variable to keep track of the balance of underlying tokens in a pod.
