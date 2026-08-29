# [M] M-03 ERC4626 Vault is vulnerable to dust front-run grief

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/132
Type: sherlock-finding

## Details
GalloDaSballo

medium

# M-03 ERC4626 Vault is vulnerable to dust front-run grief

## Summary

Because ERC4626 checks for totalSupply and totalAssets, it is susceptible to a rebase attack.


https://github.com/solidstate-network/solidstate-solidity/blob/9a99628af2daacc26929f84ff29a6a30ae365d8d/contracts/token/ERC4626/base/ERC4626BaseInternal.sol#L41

## Vulnerability Detail

By depositing less than `ONE_SHARE` of underlying, it's possible to have an initial mint of less than `ONE_SHARE` of shares.

Via a direct transfer of underlying the Shares Price Per Share can then be inflated, which will cause losses to future depositors.

This is a well known attack, and at this time the best remediation is for the team to seed an initial basic deposit to avoid the rebase being enacted in the wild.

## Impact

After the share have been rebased, new depositors will receive less shares than expected, causing loss at the advantage of the early depositors

## Code Snippet

## Tool used

Manual Review

## Recommendation

A clear mitigation has yet to be shown, Yearn may address it in V3.

A ONE_SHARE deposit logically sounds like a good start, however in practice certain LP tokens will not allow you to mint that much, meaning a lower threshold may be realistic but may also allow the attack to happen.



_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/132_
