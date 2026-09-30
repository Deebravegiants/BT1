# [M] Presence of delegate not enforced

## Summary
Severity: Medium
Contest weight: 0.5569
Dataset id: 6840
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A delegate address on the destination chain can be used to fix stuck transactions by changing the slippage limits and by re-executing transactions. However, the presence of a delegate address isn't checked in _xcall().
Note: set to medium risk because tokens could get lost

```solidity
function forceUpdateSlippage(TransferInfo calldata _params, uint256 _slippage) external onlyDelegate(_params) {
    ...
}
```

```solidity
function execute(ExecuteArgs calldata _args) external nonReentrant whenNotPaused returns (bytes32) {
    (bytes32 transferId, DestinationTransferStatus status) = _executeSanityChecks(_args);
    ...
}
```

```solidity
function _executeSanityChecks(ExecuteArgs calldata _args) private view returns (bytes32, DestinationTransferStatus) {
    // If the sender is not approved relayer, revert
    if (!s.approvedRelayers[msg.sender] && msg.sender != _args.params.delegate) {
        revert BridgeFacet__execute_unapprovedSender();
    }
}
```

## Recommendation
Enforce the presence of a delegate address in _xcall(). Or at least document the behavior explicitly.
