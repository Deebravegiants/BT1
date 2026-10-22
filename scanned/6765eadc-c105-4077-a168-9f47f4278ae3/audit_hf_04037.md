# [H] recipientsCounter should start from 1 in

## Summary
Severity: High
Contest weight: 0.9793
Dataset id: 20469
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DonationVotingMerkleDistributionBaseStrategy._registerRecipient calls _getUintRecipientStatus to get the current status of the application. The status of the new application should be Status.None. Then, the recipientToStatusIndexes[recipientId] to recipientsCounter and allo-v2/contracts/strategies/donation-voting-merkle-base/DonationVotingMerkleDistributionBaseStrategy.sol#L580

```solidity
function _registerRecipient(bytes memory _data, address _sender)
    internal
    override
    onlyActiveRegistration
    returns (address recipientId)
{
    uint8 currentStatus = _getUintRecipientStatus(recipientId);
    if (currentStatus == uint8(Status.None)) {
        // recipient registering new application
        recipientToStatusIndexes[recipientId] = recipientsCounter;
        _setRecipientStatus(recipientId, uint8(Status.Pending));
        bytes memory extendedData = abi.encode(_data, recipientsCounter);
        emit Registered(recipientId, extendedData, _sender);
        recipientsCounter++;
    } else {
        if (currentStatus == uint8(Status.Accepted)) {
            // recipient updating accepted application
            _setRecipientStatus(recipientId, uint8(Status.Pending));
        } else if (currentStatus == uint8(Status.Rejected)) {
            // recipient updating rejected application
            _setRecipientStatus(recipientId, uint8(Status.Appealed));
        }
        emit UpdatedRegistration(recipientId, _data, _sender, _getUintRecipientStatus(recipientId));
    }
}
```

DonationVotingMerkleDistributionBaseStrategy._getUintRecipientStatus calls _getStatusRowColumn to get the column index and current row. https://github.com/sting-merkle-base/DonationVotingMerkleDistributionBaseStrategy.sol#L819

```solidity
function _getUintRecipientStatus(address _recipientId) internal view returns (uint8 status) {
    // Get the column index and current row
    (, uint256 colIndex, uint256 currentRow) = _getStatusRowColumn(_recipientId);
    // Get the status from the 'currentRow' shifting by the 'colIndex'
    status = uint8((currentRow >> colIndex) & 15);
    // Return the status
    return status;
}
```

DonationVotingMerkleDistributionBaseStrategy._getStatusRowColumn computes indexes from recipientToStatusIndexes[_recipientId]. For the new recipient. blob/main/allo-v2/contracts/strategies/donation-voting-merkle-base/DonationVotingMerkleDistributionBaseStrategy.sol#L833

```solidity
function _getStatusRowColumn(address _recipientId) internal view returns (uint256, uint256, uint256) {
    uint256 recipientIndex = recipientToStatusIndexes[_recipientId];
    uint256 rowIndex = recipientIndex / 64; // 256 / 4
    uint256 colIndex = (recipientIndex % 64) * 4;
    return (rowIndex, colIndex, statusesBitMap[rowIndex]);
}
```

erkle-base/DonationVotingMerkleDistributionBaseStrategy.sol#L166

```solidity
/// @notice The total number of recipients.
uint256 public recipientsCounter;
```

Consider the following situation:
• Alice is the first recipient calls registerRecipient
// in _registerRecipient
recipientToStatusIndexes[Alice] = recipientsCounter = 0;
_setRecipientStatus(Alice, uint8(Status.Pending));
recipientCounter++
• Bob calls registerRecipient.
// in _getStatusRowColumn
recipientToStatusIndexes[Bob] = 0 // It would access the status of Alice
// in _registerRecipient
currentStatus = _getUintRecipientStatus(recipientId) = Status.Pending
currentStatus != uint8(Status.None) -> no new application is recorded in the pool.

This implementation error makes the pool can only record the first application.

## Recommendation
Make the counter start from 1. There are two methods to fix the issue.
1.
```solidity
/// @notice The total number of recipients.
uint256 public recipientsCounter;
```
2.
```solidity
function _registerRecipient(bytes memory _data, address _sender)
    internal
    override
    onlyActiveRegistration
    returns (address recipientId)
{
    ...
    uint8 currentStatus = _getUintRecipientStatus(recipientId);
    if (currentStatus == uint8(Status.None)) {
        // recipient registering new application
        recipientToStatusIndexes[recipientId] = recipientsCounter + 1;
        _setRecipientStatus(recipientId, uint8(Status.Pending));
        bytes memory extendedData = abi.encode(_data, recipientsCounter);
        emit Registered(recipientId, extendedData, _sender);
        recipientsCounter++;
    ...
}
```
