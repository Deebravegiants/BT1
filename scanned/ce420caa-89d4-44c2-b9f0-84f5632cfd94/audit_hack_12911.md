# [M] Interest configuration logic always fails

## Summary
Severity: Medium
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1282-L1291
Type: audit-issue

## Details
# Interest configuration logic always fails

## Summary
The `Vault` contract has some logic to choose between to use the contract's interest configuration or a fallback configuration. But the logic used to decide which one to use is wrong.

## Vulnerability Detail
In the `Vault` contract, there is the function `_interest_configuration` which receives an address and depending on if it has some interest configuration or not, it returns the account configuration or the fallback one stored in the contract.

But the thing is the logic to choose is wrong. It should return the fallback configuration if any of the account configuration values is 0 and otherwise it should return the account configuration. But currently it is returning always the account configuration unless the account has a correctly configured interest configuration, then it will return the fallback one.

## Impact
Although the function is not being called right now by any other function, since it is in the scope of the audit and it has a wrong logic, it is important to fix it since it the issue is not corrected and in the future this function is called, it could break all the functions that use the interest configuration, like `_dynamic_interest_rate_low_utilization`, `_dynamic_interest_rate_high_utilization`, `_interest_rate_by_utilization`, `_current_interest_per_second`, `current_interest_per_second`, `_debt_interest_since_last_update`, `_total_debt_plus_pending_interest`, `_amount_per_debt_share`, `_debt_shares_to_amount`, `debt_shares_to_amount`, `_debt`, `debt`....

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1282-L1291

## Tool used
Manual Review

## Recommendation
Change the logic of the `if` condition to something like this:
```vyper
if (
        self.interest_configuration[_address][0] == 0
        or self.interest_configuration[_address][1] == 0
        or self.interest_configuration[_address][2] == 0
        or self.interest_configuration[_address][3] == 0
    ):
        return FALLBACK_INTEREST_CONFIGURATION

    return self.interest_configuration[_address]
```
