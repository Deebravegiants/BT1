# [M] Bypassable checkLastBlockAction Modifier

## Summary
Severity: Medium
Contest weight: 0.5600
Dataset id: 13948
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The checkLastBlockAction modifier is intended to prevent users from depositing and withdrawing in the same block, likely as a measure against flash loan attacks. However, this check can be easily bypassed. A user can deposit and receive share tokens, then transfer these shares to another address they control and proceed to withdraw in the same block from that address.
```solidity
modifier checkLastBlockAction() {
    (_callerLastBlockAction[msg.sender] == block.number) revert UniV3TokenizedLp_NoDepositSameBlock();
    _callerLastBlockAction[msg.sender] = block.number;
}
...
function deposit(
    uint256 deposit0,
    uint256 deposit1,
    address to
) external override nonReentrant checkLastBlockAction returns (uint256 shares) {
...
function withdraw(
    uint256 shares,
    address to
) external override nonReentrant checkLastBlockAction returns (uint256 amount0, uint256 amount1) {
```

## Recommendation
To address this issue, override the _afterTokenTransfer function to update the _callerLastBlockAction mapping for the to address. This ensures that the restriction on block actions applies consistently, even when tokens are transferred between addresses.
```solidity
function _afterTokenTransfer(address from, address to, uint256 amount) internal override {
    super._afterTokenTransfer(from, to, amount);
    _callerLastBlockAction[to] = block.number;
}
```
