# [M] Proper Initialization Enforcement In sOlympus::setStakingContract()

## Summary
Severity: Medium
Contest weight: 0.3733
Dataset id: 12584
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function setStakingContract(
    address newStakingContract_
) external onlyOwner() {
    stakingContract = newStakingContract_;
    _gonBalances[stakingContract] = TOTAL_GONS;
}
```
While it indeed properly sets up the stakingContract address and initializes the Gon balance, this initialization operation should only occur once. Otherwise, the sOHM supply may go awry, resulting in protocol-wide instability.

## Recommendation
Ensure the setStakingContract() can only be initialized once.
