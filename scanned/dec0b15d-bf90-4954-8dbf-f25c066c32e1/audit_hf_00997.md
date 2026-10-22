# [M] Fee on Transfer Token Will Break accounting

## Summary
Severity: Medium
Contest weight: 0.4037
Dataset id: 3308
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
mint()/deposit() is using amount for transfering and accounting. But fee on transfer token could break the accounting, since the actual token received will be less than amount. As a result, sharePrice will have some small error each time.
File: src\abstract\As4626.sol
```solidity
function mint(
    uint256 _shares,
    address _receiver
) public returns (uint256 assets) {
    return _deposit(previewMint(_shares), _shares, _receiver);
}

function deposit(
    uint256 _amount,
    address _receiver
) public whenNotPaused returns (uint256 shares) {
    return _deposit(_amount, previewDeposit(_amount), _receiver);
}

function _deposit(
    uint256 _amount,
    uint256 _shares,
    address _receiver
) internal nonReentrant returns (uint256) {
    asset.safeTransferFrom(msg.sender, address(this), _amount);
    _mint(_receiver, _shares);
}
```
USDT potentially could turn on fee on transfer feature, but not yet.

## Recommendation
Use before and after balance to accurately reflect the true amount received, and update share price accordingly.
