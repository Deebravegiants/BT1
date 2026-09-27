# [M] Manipulations of setFee

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L104-L113
Type: audit-issue

## Details
# Lines of code

https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L104-L113
https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L164
https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L213
https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L256


# Vulnerability details

## Impact
If we consider that the fee variable is meaningfully applied, there will still be several problems with this:
1) Admin can setFee up to 100%. This is bad for users, fees should have a reasonable upper limit, e.g. 30% to prevent potential griefing.
2) Tokens are transferred in a separate function called transferBribes, which means that depositBribe txs have already settled. setFee can happen anytime, so an admin can change fees for already made deposits. I think this is again bad for users, as you need extra trust on an admin to not exploit this, and smart contracts should aim for as little external trust as possible.
3) Even if a fee would be applied in depositBribe, function setFee could frontrun user deposits. Consider using a timelock, so that users have time to react and adjust.
