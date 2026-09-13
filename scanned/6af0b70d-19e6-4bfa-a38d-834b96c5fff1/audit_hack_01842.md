# [M] Rename functions

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
The naming of the functions should reflect their nature, such as functions starting with “get” should be only getters and do not change state. This will result in confusion developments and the implicit state changes might not be noticed.

Other than getters, some other function or variable names are misleading. 

#### Examples
The following functions are a few examples that are named as getters but they change the state. 

- getState -> updateState
   - getDelegationsTotal
   - getDelegationsForValidator
   - getDelegationsByHolder

Some other naming that does not reflect the nature of the functionality:

- getPurchasedAmount -> getPurchasedUnlocked
- tokenState.Sold -> lock

#### Recommendation
For functions that get and update variables use `getAndUpdate` naming. Similarly use variable names that reflect the nature of the values they store.
