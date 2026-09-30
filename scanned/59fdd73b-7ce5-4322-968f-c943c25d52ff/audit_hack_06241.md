# [M] Break contract functionalities

## Summary
Severity: Medium
Reporter: csanuragjain
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L604
Type: audit-issue

## Details
# Break contract functionalities

## Summary
It is possible for operator to remove himself. This will have the contract without any operator. This becomes problem since all functionalities requiring operator role will stop working

## Vulnerability Detail
1. Operator O1 is existing
2. Operator O1 removes itself by calling `remove_operator` function

```solidity
def remove_operator(_to_remove: address):
    """
    @notice
        Remove an existing operator from the priviledged addresses.
    """
    assert self.is_operator[msg.sender], "unauthorized"
    assert self.is_operator[_to_remove], "not an operator"

    self.is_operator[_to_remove] = False

    log OperatorRemoved(_to_remove, msg.sender)
```

3. Now no operator is present in contract. 
4. This directly impact function like `add_depositor` , `set_alchemist` , `set_fund_receiver` etc which cannot be called now (callable by operator only)

## Impact
Any functionality requiring operator role will not work

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L604

## Tool used
Manual Review

## Recommendation
operator should not be allowed to remove himself and one operator should always remain in system
