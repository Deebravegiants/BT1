# [M] Bonuses can't be applied

## Summary
Severity: Medium
Contest weight: 0.3943
Dataset id: 6226
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BonusesL3 contract expects to hold ETH in its balance to later distribute it but it lacks a receive function:
```solidity
function distribute(address to, uint256 amount) internal nonReentrant returns (bool) {
    if (to == address(0)) {
        emit DistributionAttempt(to, amount, false, "Invalid address");
        return false;
    }
    if (amount == 0) {
        emit DistributionAttempt(to, amount, false, "Invalid amount");
        return false;
    }
    if (address(this).balance < amount) {
        emit DistributionAttempt(to, amount, false, "Insufficient balance");
        return false;
    }
    (bool success, ) = to.call{value: amount}("");
    emit DistributionAttempt(to, amount, success, success ? "Success" : "Payment failed");
    return success;
}
```

## Recommendation
Add a receive function inside the BonusesL3 contract.
