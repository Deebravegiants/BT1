# [M] M-8 GovernanceProxy DOS via updateDelay()

## Summary
Severity: Medium
Contest weight: 0.4087
Dataset id: 6777
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If an admin mistakenly calls updateDelay(someImportantFunction, SUPERBIGNUMBER) in GovernanceProxy, restoring a lower delay for someImportantFunction becomes impossible. To execute updateDelay(someImportantFunction, LOW_NUMBER), one would need to wait out the initially set SUPERBIGNUMBER delay:
```solidity
function _computeDelay(
    bytes calldata data
) internal view returns (uint64) {
    bytes4 selector = bytes4(data[:4]);
    // special case for updateDelay, we want to set the delay
    // as the delay for the current function for which the delay
    // will be changed, rather than a generic delay for updateDelay itself
    // for all the other functions, we use their actual delay
    if (selector == GovernanceProxy.updateDelay.selector) {
        bytes memory callData = data[4:];
        (selector, ) = abi.decode(callData, (bytes4, uint256));
    }
    return delays[selector];
}
```
GovernanceProxy.sol#L196-L210
In this situation, function calls might effectively get blocked for an excessively long period.

## Recommendation
We recommended capping the maximum delay at a reasonable number.
