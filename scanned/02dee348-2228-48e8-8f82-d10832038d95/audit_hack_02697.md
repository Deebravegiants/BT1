# [M] [NAZ-M4] Vault Admin can Front-Run Users Changing `PerformanceFee && withdrawalFee` Due To Missing Time Locks

## Summary
Severity: Medium
Reporter: 0xNazgul
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L155
Type: audit-issue

## Details
# [NAZ-M4] Vault Admin can Front-Run Users Changing `PerformanceFee && withdrawalFee` Due To Missing Time Locks

## Summary
When critical parameters of systems need to be changed, it is required to broadcast the change via event emission and recommended to enforce the changes after a time-delay. 

## Vulnerability Detail
This is to allow system users to be aware of such critical changes and give them an opportunity to exit or adjust their engagement with the system accordingly. None of the onlyOwner functions that change critical protocol addresses/parameters have a timelock for a time-delayed change to alert: (1) users and give them a chance to engage/exit protocol if they are not agreeable to the changes (2) team in case of compromised owner(s) and give them a chance to perform incident response.

## Impact
A vault admin could front-run users changing the fees when doing major withdrawals changing users more then what they thought.

## Code Snippet
[`VaultAdmin.sol#L155`](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L155), [`VaultAdmin.sol#L175`](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L175)

## Tool used
Manual Review

## Recommendation
Consider adding time locks to these functions to give users time to adjust positions and prevent malicious vault admins from front-running users.
