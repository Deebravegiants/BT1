# [H] TWAP address in Dca.vy is wrong and unusable.

## Summary
Severity: High
Reporter: BugBusters
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49
Type: audit-issue

## Details
# TWAP address in Dca.vy is wrong and unusable.

## Summary
Adress used for TWAP in Dca.vy is not deployed and don't exist on arbitrum.
## Vulnerability Detail
Contract Dca.vy uses the address constant of TWAP: constant(address) = 0xFa64f316e627aD8360de2476aF0dD9250018CFc5 , to call the TWAP specific functions like `getTwap` but the problem is this address doesn't exist on the arbitrum network and nothing is deployed there hence make the Dca.vy compeltely unusable.

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49

```solidity
TWAP: constant(address) = 0xFa64f316e627aD8360de2476aF0dD9250018CFc5 
```

## Impact
Dca.vy is not  usable in current state.
## Code Snippet
```solidity
TWAP: constant(address) = 0xFa64f316e627aD8360de2476aF0dD9250018CFc5 
```
## Tool used

Manual Review

## Recommendation
Use the correct address that is: https://arbiscan.io/address/0x9edB86AdC192931390EF9c262Db651bA1945Dc52#readContract
