# [M] Not compatible with Rebasing/Deflationary/Inflationary tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-skale
Published: 2022-03-03
Source: https://github.com/code-423n4/2022-02-skale-findings/issues/50
Type: code-finding

## Details
# Lines of code

https://github.com/skalenetwork/ima-c4-audit/blob/11d6a6ae5bf16af552edd75183791375e501915f/contracts/mainnet/DepositBoxes/DepositBoxERC20.sol#L299-L308


# Vulnerability details

## Proof of Concept
The `DepositBoxERC20` contract do not appear to support rebasing/deflationary/inflationary tokens whose balance changes during transfers or over time. The necessary checks include at least verifying the amount of tokens transferred to contracts before and after the actual transfer to infer any fees/interest.

## Recommended Mitigation Steps
Add support in contracts for such tokens before accepting user-supplied tokens
Consider to check before/after balance on the vault.
