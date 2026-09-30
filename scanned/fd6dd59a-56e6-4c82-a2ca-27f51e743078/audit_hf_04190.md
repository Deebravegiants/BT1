# [M] `maxDeposit`

## Summary
Severity: Medium
Contest weight: 0.1331
Dataset id: 20956
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability lies in the implementation of the maxDeposit view function of the PrizeVault contract. The function reports the maximum amount that can be deposited by calling yieldVault.maxDeposit(address(this)). However, the actual deposit path used by the contract is _depositAndMint, which calls yieldVault.mint(). The mint function may impose a lower ceiling than the deposit function, because minting is limited by the amount of shares that can be minted, which can be constrained by the vault's total supply or other internal caps. As a result, maxDeposit can return a value that exceeds the amount that can be successfully minted, causing a deposit transaction that attempts to use the reported maxDeposit to revert. This violates the expectations of EIP‑4626, which requires that maxDeposit reflect the true upper bound for a successful deposit. An attacker or honest user could trigger the revert by simply trying to deposit the advertised maximum, leading to a failed transaction, loss of gas, and a confusing user experience where the UI shows a positive deposit limit but the blockchain rejects the operation. The issue appears when the underlying yieldVault imposes a stricter mint limit than deposit limit, which can happen after certain state changes such as reaching a share cap or after a large previous mint. The affected parties are any user of the PrizeVault who relies on the maxDeposit value to determine how much they can deposit, as well as the protocol that may lose confidence due to inconsistent accounting. The bug was discovered during a static audit that compared the contract's public view functions against the EIP‑4626 specification and identified the mismatch between maxDeposit and the internal mint call. It can be hard to notice because the view function itself does not revert and returns a plausible number, while the failure only occurs at runtime when a deposit is attempted. The proper fix is to compute the maximum deposit based on the same constraints used by the mint path, for example by calling yieldVault.previewRedeem(yieldVault.maxMint()) or by directly querying the mint limit and converting it to a deposit amount. Aligning the reported limit with the actual mintable amount restores compliance with EIP‑4626 and prevents users from encountering unexpected reverts.

## Proof of Concept
[`maxDeposit()` returns up to `yieldVault.maxDeposit(address(this))`](https://github.com/code-423n4/2024-03-pooltogether/blob/480d58b9e8611c13587f28811864aea138a0021a/pt-v5-vault/src/PrizeVault.sol#L374-L392). However, [`_depositAndMint()` deposits using `yieldVault.mint()`](https://github.com/code-423n4/2024-03-pooltogether/blob/480d58b9e8611c13587f28811864aea138a0021a/pt-v5-vault/src/PrizeVault.sol#L866) which may have a stricter limit than `yieldVault.deposit()`. In that case depositing `maxDeposit()` would revert, which violates EIP-4626.

## Recommendation
Use `yieldVault.previewRedeem(yieldVault.maxMint())`.
