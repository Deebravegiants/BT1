# [M] Attacker can DOS privateMint()

## Summary
Severity: Medium
Contest weight: 0.0982
Dataset id: 7434
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function privateMint() calls permit() to set the allowance before token transfer:
IERC20Permit(address(paymentToken)).permit(permit.owner, address(this), permit.value, permit.deadline, v, r, s);
usdPlusAmount = permit.value;
_issue(
paymentToken,
permit.value,
permit.value,
permit.owner,
permit.owner
);
The issue is that the attacker can watch the mempool and use the signature to call permit and it would cause the original transaction to revert because of the used nonce. As a result, the attacker can DOS the calls to privateMint() function. The same issue exists in selfPermit() function too.

## Recommendation
Use try/catch when calling permit and if the current allowance is bigger than the spending amount allow logic to be executed. link
