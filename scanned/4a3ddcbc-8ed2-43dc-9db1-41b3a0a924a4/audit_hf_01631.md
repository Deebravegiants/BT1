# [M] Vulnerability in startPresale function allows indefinite token lock

## Summary
Severity: Medium
Contest weight: 0.1376
Dataset id: 8756
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The startPresale function in the HolofairToken contract is designed to initiate the presale process, setting the presaleActive state to true and establishing the fundraisingEndTime based on the current block timestamp and the predefined fundraisingPeriod. However, the function lacks a critical check to ensure that the presale has not already been marked as successful (presaleSuccess is false). This oversight allows a malicious creator to restart the presale even after it has concluded successfully and liquidity has been migrated to Uniswap V2. By doing so, the creator can lock the tokens indefinitely, as both the claimTokens and claimTeamTokens functions require presaleActive to be false for token claiming to proceed. Furthermore, by calling pausePresale followed by startPresale the creator is able to extend the presale duration, allowing the creator to lock the tokens indefinitely.

## Recommendation
To prevent the indefinite locking of tokens, introduce a check in the startPresale function to ensure that presaleSuccess is false before allowing the presale to be restarted.
