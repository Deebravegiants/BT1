# [M] ChainlinkFactory will pay non-requested ver sions

## Summary
Severity: Medium
Contest weight: 0.6935
Dataset id: 22668
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Protocol definition: Requested versions will pay out a keeper fee,
non-requested versions will not. But ChainlinkFactory ignores numRequested,
which pays for both.
Vulnerability Details
Protocol definition: Requested versions will pay out a keeper fee,
non-requested versions will not.
```solidity
/// @notice Commits the price to specified version
/// @dev Accepts both requested and non-requested versions.
///
/// Requested versions will pay out a keeper fee, non-requested versions will not.
///
/// Accepts any publish time in the underlying price message, as long as it
/// is within the validity window,
///
/// which means its possible for publish times to be slightly out of order
/// with respect to versions.
///
/// Batched updates are supported by passing in a list of price feed ids
/// along with a valid batch update data.
/// @param ids The list of price feed ids to commit
/// @param version The oracle version to commit
/// @param data The update data to commit
function commit(bytes32[] memory ids, uint256 version, bytes calldata data)
external payable {
    ...
}
```
commit()->_handleKeeperFee()->_applicableValue()
ChainlinkFactory._applicableValue () implements the following:
```solidity
function _applicableValue(uint256, bytes memory data) internal view override
returns (uint256) {
    bytes[] memory payloads = abi.decode(data, (bytes[]));
    uint256 totalFeeAmount = 0;
    for (uint256 i = 0; i < payloads.length; i++) {
        (Asset memory fee, ,) = feeManager.getFeeAndReward(address(this),
            payloads[i]);
        totalFeeAmount += fee.amount;
    }
    return totalFeeAmount;
}
```
The above method ignores the first parameter numRequested. This way, whether it is
Requested versions or not, you will pay keeper fees. Violating non-requested
versions will not pay
If non-requested versions will pay as well, it is easy to maliciously submit
needs at least one numRequested to call _handleKeeperFee() )

## Recommendation
It is recommended that only Requested versions keeper fees'
```solidity
function _applicableValue(uint256 , bytes memory data) internal view
override returns (uint256) {
    bytes[] memory payloads = abi.decode(data, (bytes[]));
    uint256 totalFeeAmount = 0;
    for (uint256 i = 0; i < payloads.length; i++) {
        (Asset memory fee, ,) = feeManager.getFeeAndReward(address(this),
            payloads[i]);
        totalFeeAmount += fee.amount;
    }
    return totalFeeAmount * numRequested / payloads.length;
}
```
