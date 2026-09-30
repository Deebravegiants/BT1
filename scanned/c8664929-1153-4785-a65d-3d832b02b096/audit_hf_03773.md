# [M] A borrower/lender or liquidator will fail to withdraw collateral due to gas limit

## Summary
Severity: Medium
Contest weight: 0.5940
Dataset id: 19951
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the TellerV2#submitBid(), there is no limitation on how many collateral assets a borrower can assign into the _collateralInfo array parameter. This leads to some bad scenarios like this due to reaching gas limit:
• A borrower or a lender fail to withdraw the collateral assets when the loan would not be liquidated.
• A liquidator will fail to withdraw the collateral assets when the loan would be liquidated.
Within the ICollateralEscrowV1, the Collateral struct would be defined like this:
```solidity
struct Collateral {
    CollateralType _collateralType;
    uint256 _amount;
    uint256 _tokenId;
    address _collateralAddress;
}
```
Within the CollateralManager, the CollateralInfo struct would be defined like this:
```solidity
/**
* Since collateralInfo is mapped (address assetAddress => Collateral) that means
* that only a single tokenId per nft per loan can be collateralized.
* Ex. Two bored apes cannot be used as collateral for a single loan.
*/
struct CollateralInfo {
    EnumerableSetUpgradeable.AddressSet collateralAddresses;
    mapping(address => Collateral) collateralInfo;
}
```
Within the CollateralManager, the _bidCollaterals storage would be defined like this:
```solidity
// bidIds -> validated collateral info
mapping(uint256 => CollateralInfo) internal _bidCollaterals;
```
When a borrower submits a bid, the TellerV2#submitBid() would be called. Within the TellerV2#submitBid(), multiple collaterals, which are ERC20/ERC721/ERC1155, can be assigned into the _collateralInfo array parameter by a borrower. And then, these collateral assets stored into the _collateralInfo array would be associated with bidId_ through internally calling the CollateralManager#commitCollateral().
```solidity
function submitBid(
    address _lendingToken,
    uint256 _marketplaceId,
    uint256 _principal,
    uint32 _duration,
    uint16 _APR,
    string calldata _metadataURI,
    address _receiver
) public override whenNotPaused returns (uint256 bidId_) {
    ...
    bool validation = collateralManager.commitCollateral(
        bidId_,
        _collateralInfo
    );
    ...
}
```
Within the CollateralManager#commitCollateral(), each collateral asset (info) would be associated with a _bidId respectively by calling the CollateralManager#_commitCollateral() in the for-loop like this:
```solidity
/**
* @notice Checks the validity of a borrower's multiple collateral balances and commits it to a bid.
* @param _bidId The id of the associated bid.
* @param _collateralInfo Additional information about the collateral assets.
* @return validation_ Boolean indicating if the collateral balances were validated.
*/
function commitCollateral(
    uint256 _bidId,
    Collateral[] calldata _collateralInfo
) public returns (bool validation_) {
    address borrower = tellerV2.getLoanBorrower(_bidId);
    (validation_, ) = checkBalances(borrower, _collateralInfo);
    if (validation_) {
        for (uint256 i; i < _collateralInfo.length; i++) {
            Collateral memory info = _collateralInfo[i];
            _commitCollateral(_bidId, info);
        }
    }
}
```
Within the CollateralManager#_commitCollateral(), the _collateralInfo would be stored into the _bidCollaterals storage like this:
```solidity
/**
* @notice Checks the validity of a borrower's collateral balance and commits it to a bid.
* @param _bidId The id of the associated bid.
* @param _collateralInfo Additional information about the collateral asset.
*/
function _commitCollateral(
    uint256 _bidId,
    Collateral memory _collateralInfo
) internal virtual {
    CollateralInfo storage collateral = _bidCollaterals[_bidId];
    collateral.collateralAddresses.add(_collateralInfo._collateralAddress);
    collateral.collateralInfo[
        _collateralInfo._collateralAddress
    ] = _collateralInfo;
    ...
}
```
When the deposited-collateral would be withdrawn by a borrower or a lender, the CollateralManager#withdraw() would be called. Within the CollateralManager#withdraw(), the CollateralManager#_withdraw() would be called.
```solidity
/**
* @notice Withdraws deposited collateral from the created escrow of a bid that has been successfully repaid.
* @param _bidId The id of the bid to withdraw collateral for.
*/
function withdraw(uint256 _bidId) external {
    BidState bidState = tellerV2.getBidState(_bidId);
    if (bidState == BidState.PAID) {
        _withdraw(_bidId, tellerV2.getLoanBorrower(_bidId));
        _withdraw(_bidId, tellerV2.getLoanLender(_bidId));
        emit CollateralClaimed(_bidId);
    } else if (tellerV2.isLoanDefaulted(_bidId)) {
        _withdraw(_bidId, tellerV2.getLoanLender(_bidId));
        emit CollateralClaimed(_bidId);
    } else {
        revert("collateral cannot be withdrawn");
    }
}
```
When the deposited-collateral would be liquidated by a liquidator, the CollateralManager#liquidateCollateral() would be called. Within the CollateralManager#liquidateCollateral(), the CollateralManager#_withdraw() would be called.
```solidity
/**
* @notice Sends the deposited collateral to a liquidator of a bid.
* @notice Can only be called by the protocol.
* @param _bidId The id of the liquidated bid.
* @param _liquidatorAddress The address of the liquidator to send the collateral to.
*/
function liquidateCollateral(uint256 _bidId, address _liquidatorAddress)
    external
    onlyTellerV2
{
    if (isBidCollateralBacked(_bidId)) {
        BidState bidState = tellerV2.getBidState(_bidId);
        require(
            bidState == BidState.LIQUIDATED,
            "Loan has not been liquidated"
        );
        _withdraw(_bidId, _liquidatorAddress);
    }
}
```
Within the CollateralManager#_withdraw(), each collateral asset (collateralInfo._collateralAddress) would be withdrawn by internally calling the ICollateralEscrowV1#withdraw() in a for-loop like this:
```solidity
/**
* @notice Withdraws collateral to a given receiver's address.
* @param _bidId The id of the bid to withdraw collateral for.
* @param _receiver The address to withdraw the collateral to.
*/
function _withdraw(uint256 _bidId, address _receiver) internal virtual {
    for (
        uint256 i = 0;
        i < _bidCollaterals[_bidId].collateralAddresses.length();
        i++
    ) {
        // Get collateral info
        Collateral storage collateralInfo = _bidCollaterals[_bidId]
            .collateralInfo[
                _bidCollaterals[_bidId].collateralAddresses.at(i)
            ];
        // Withdraw collateral from escrow and send it to bid lender
        ICollateralEscrowV1(_escrows[_bidId]).withdraw(
            collateralInfo._collateralAddress,
            collateralInfo._amount,
            _receiver
        );
    }
}
```
However, within the TellerV2#submitBid(), there is no limitation on how many collateral assets a borrower can assign into the _collateralInfo array parameter. This leads to a bad scenario like below:
• A borrower assigns too many collateral assets (ERC20/ERC721/ERC1155) into the _collateralInfo array parameter when the borrower calls the TellerV2#submitBid() to submit a bid.
• Then, a lender accepts the bid via calling the TellerV2#lenderAcceptBid().
• Then, a borrower or a lender try to withdraw the collateral, which is not liquidated, by calling the CollateralManager#withdraw(). Or, a liquidator tries to withdraw the collateral, which is liquidated, by calling the CollateralManager#liquidateCollateral().
• But, the transaction of the CollateralManager#withdraw() or the CollateralManager#liquidateCollateral() will be reverted in the for-loop of the CollateralManager#_withdraw() because that transaction will reach a gas limit.
Due to reaching gas limit, some bad scenarios would occur like this:
• A borrower or a lender fail to withdraw the collateral assets when the loan would not be liquidated.
• A liquidator will fail to withdraw the collateral assets when the loan would be liquidated.

## Recommendation
Within the TellerV2#submitBid(), consider adding a limitation about how many collateral assets a borrower can assign into the _collateralInfo array parameter.
