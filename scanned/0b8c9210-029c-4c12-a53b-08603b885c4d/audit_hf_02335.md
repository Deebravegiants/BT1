# [M] Incorrect Fee Withdraw Logic in PanzLending::withdrawFee()

## Summary
Severity: Medium
Contest weight: 0.5540
Dataset id: 12687
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PanzLending contract provides an external withdrawFee() function for the privileged owner account to claim the platform fee from the contract. While reviewing its logic, we notice the current implementation is not correct.
To elaborate, we show below the related code snippet.
It comes to our attention that the feeBalance is reset to 0 before the fee is sent to the msg.sender (line 76). Thus the fee claimed by the msg.sender is always 0 (line 77).
```solidity
/**
 * @dev claim platform fee
 */
function withdrawFee() external onlyOwner nonReentrant {
    if (feeBalance == 0) revert InsufficientBalance();
    feeBalance = 0;
    (bool success,) = payable(msg.sender).call{value: feeBalance}("");
    if(!success) revert PaymentFailed();
}
```

## Recommendation
Define a temporary variable to store the feeBalance before it is set to 0. An example revision is shown as follows:
```solidity
/**
 * @dev claim platform fee
 */
function withdrawFee() external onlyOwner nonReentrant {
    uint256 fee = feeBalance;
    if (fee == 0) revert InsufficientBalance();
    feeBalance = 0;
    (bool success,) = payable(msg.sender).call{value: fee}("");
    if(!success) revert PaymentFailed();
}
```
