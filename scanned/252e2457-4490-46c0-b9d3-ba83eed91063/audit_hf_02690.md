# [M] Price Inflation Of cTokenShare When Supply Is Zero

## Summary
Severity: Medium
Contest weight: 0.1441
Dataset id: 14552
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the current supply is zero, an attacker can perform a share inflation attack during delegation.
This can be illustrated through the following steps:
1. Alice wants to delegate 1 SD token (which has 18 decimals) to the utility pool calling delegate().
2. The pool is empty. The exchange rate is the default 1 SD per cTokenShare.
3. Bob sees Alice’s transaction in the mempool and decides to sandwich it.
4. Bob delegates 1 wei of SD and receives 1 wei of cTokenShare in exchange. The exchange rate is now 1 SD per cTokenShare.
5. Bob transfers 1 SD (1e18 wei) to the vault using an ERC-20 transfer. No new cTokenShares are created. Hence, the exchange rate is now 1e18 + 1 SD per cTokenShare, or 1e18 + 1 wei of SD per wei of cTokenShare.
6. Alice’s deposit is executed. Her 1e18 wei of SD tokens are worth less than 1 wei of cTokenShare. Therefore, the contract takes the assets, but does not add shares. Alice has effectively "donated" her tokens.

## Recommendation
Consider implementing a decimal offset virtual shares and assets to the pool.
See the following for more details: Addressing Inflation Attacks With Virtual Shares And Assets
