# [M] 6.3 Governance Can Burn From Users

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed Risk Accepted

The function ClaimFee.withdraw() allows the privileged ward role (the governance) to burn a claim
of any user. However, the function's annotation contradicts this as it states the following:

```
/// Withdraws claim balance held by governance before maturity
/// @dev Governance is allowed to burn the balance it owns
```

Furthermore, this function can also withdraw/burn a claim balance upon/after maturity.

Risk accepted:

The annotation was changed to reflect the functionality. The risk of allowing the governance to burn any
user's balance is accepted, as they plan to add additional contracts with functionalities that require
burning claim fee balances.
