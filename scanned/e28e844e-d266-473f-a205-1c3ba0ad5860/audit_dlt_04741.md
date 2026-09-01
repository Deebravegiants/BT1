# [M] VaultAdmin#processAuction: Must approve 0 first

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/109
Type: sherlock-finding

## Details
cccz

medium

# VaultAdmin#processAuction: Must approve 0 first

## Summary
VaultAdmin#processAuction: Must approve 0 first
## Vulnerability Detail
Some tokens (like USDT) do not work when changing the allowance from an existing non-zero allowance value. They must first be approved by zero and then the actual allowance must be approved.
## Impact
processAuction() may get stuck
## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L300-L314
## Tool used

Manual Review

## Recommendation
```diff
+                ERC20.approve(
+                    address(Pool),
+                    0
+                );
                ERC20.approve(
                    address(Pool),
                    totalCollateralUsed + _totalReserves()
                );
```

Duplicate of #136
