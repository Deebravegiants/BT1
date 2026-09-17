# [M] All operators can be removed, leaving the Vault without core functionality

## Summary
Severity: Medium
Reporter: ABA
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L604
Type: audit-issue

## Details
# All operators can be removed, leaving the Vault without core functionality

## Summary

All operators can be remove leaving the Vault without core functionality, including the setting of fund receiver (from the auction), updating alchemist or adding depositors to it.

## Vulnerability Detail

[remove_operator](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L604) from `Vault.vy` does not check if there are any operators left after removing the specific target. Mistakenly removing all operators will break core functionality.

## Impact

A `Vault` without any operator can not use core functionalities such as
- [set_alchemist](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L488)
- [set_fund_receiver](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L498)
- [add_depositor](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L618)


and other helper function:
- [add_operator](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L590)
- [remove_operator](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L604)
- [remove_depositor](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L632)

## Code Snippet

All the above functions check for operators:
```Python
assert self.is_operator[msg.sender], "unauthorized"
```

## Tool used

Manual Review

## Recommendation

Add check for an operator to not be able to remove himself.

```Python
@external
def remove_operator(_to_remove: address):
    """
    @notice
        Remove an existing operator from the priviledged addresses.
    """
    assert self.is_operator[msg.sender], "unauthorized"
    assert self.is_operator[_to_remove], "not an operator"
+   assert _to_remove != msg.sender, "cannot remove self"

    self.is_operator[_to_remove] = False

    log OperatorRemoved(_to_remove, msg.sender)
```

This fix does not prevent a coordinated malicious group of even count operators removing themselves all at the same time, but that case implies malice but the operators are considered trusted. However the fix above does save the protocol in case of mistaken removal of all operators.
