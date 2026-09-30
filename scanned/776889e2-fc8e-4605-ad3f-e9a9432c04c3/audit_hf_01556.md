# [M] Guardian can't unpause the RelayerV2

## Summary
Severity: Medium
Contest weight: 0.3785
Dataset id: 8334
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the docs, Guardian should be able to pause/unpause the protocol. Guard : Able to pause/unpause the protocol and quarantine assets. The issue is that the unpause functions access controls don't allow Guardian to unpause the protocol.
```solidity
/// @notice Unpause the protocol
function unpauseProtocol() external onlyOwner {
    paused = false;
    emit Unpause(block.timestamp);
}
/// @notice Unpause the swaps
function unpauseSwap() external onlyOwner {
    swapPaused = false;
    emit Unpause(block.timestamp);
}
```

## Recommendation
Allow Guardian to unpause the protocol.
