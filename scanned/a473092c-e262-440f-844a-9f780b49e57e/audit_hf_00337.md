# [M] Manipulations of `setFee`

## Summary
Severity: Medium
Contest weight: 0.2045
Dataset id: 1659
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[BribeVault.sol#L104-L113](https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L104-L113)  
[BribeVault.sol#L164](https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L164)  
[BribeVault.sol#L213](https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L213)  
[BribeVault.sol#L256](https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L256)  

If we consider that the fee variable is meaningfully applied, there will still be several problems with this:

  1. Admin can setFee up to 100%. This is bad for users, fees should have a reasonable upper limit, e.g. 30% to prevent potential griefing.
  2. Tokens are transferred in a separate function called transferBribes, which means that depositBribe txs have already settled. setFee can happen anytime, so an admin can change fees for already made deposits. I think this is again bad for users, as you need extra trust on an admin to not exploit this, and smart contracts should aim for as little external trust as possible.
  3. Even if a fee would be applied in depositBribe, function setFee could frontrun user deposits. Consider using a timelock, so that users have time to react and adjust.

We will likely set an upper bound as recommended, to ease user concerns. The admin being the Redacted multisig should also instill much trust and address most concerns.

The warden identified a potential admin privilege that would allow to set the fee to 100%.

I agree with the finding and severity.

## Recommendation
No recommendation
