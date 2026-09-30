# [M] SafeERC20.safeApprovereverts for changing ex-

## Summary
Severity: Medium
Contest weight: 0.4248
Dataset id: 20238
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SafeERC20.safeApprove reverts when a non-zero approval is changed to a non-zero approval. The CrosschainDistributor._setTotal function tries to change an existing approval to a non-zero value which will revert. The safeApprove function has explicit warning: // safeApprove should only be called when setting an initial allowance, // or when resetting it to zero. To increase and decrease it, use // 'safeIncreaseAllowance' and 'safeDecreaseAllowance' But still the _setTotal use it to change approval amount:
```solidity
function _allowConnext(uint256 amount) internal {
    token.safeApprove(address(connext), amount);
}
/** Reset Connext allowance when total is updated */
function _setTotal(uint256 _total) internal virtual override onlyOwner {
    super._setTotal(_total);
    _allowConnext(total - claimed);
}
```
Due to this bug all calls to setTotal function of CrosschainContinuousVestingMerkle and CrosschainTrancheVestingMerkle will get reverted. Tokensoft airdrop protocol is meant to be used by other protocols and the ability to change total parameter is an intended offering. This feature will be important for those external protocols due to the different nature & requirement of every airdrop. But this feature will not be usable by airdrop owners due to the incorrect code implementation.

## Recommendation
Consider using 'safeIncreaseAllowance' and 'safeDecreaseAllowance' instead of safeApprove in _setTotal.
