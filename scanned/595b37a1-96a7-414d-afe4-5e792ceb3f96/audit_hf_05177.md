# [M] manipulation of the Utilization

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 23245
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user with a significant number of NFTs can manipulate the totalSupply of ERC20 tokens to indirectly push protected listings towards liquidation by influencing the utilizationRate and associated. The vulnerability arises from the ability of a user to deposit and redeem any quantities of NFTs, without fees. As shown in the locker.sol contract: - the deposit function increase the totalSupply by mint function.
```solidity
function deposit(address _collection, uint[] calldata _tokenIds, address _recipient) public {
    ICollectionToken token = _collectionToken[_collection];
    token.mint(_recipient, tokenIdsLength * 1 ether * 10 ** token.denomination());
}
```
- and decrease the totalSupply using the redeem function.
```solidity
function redeem(address _collection, uint[] calldata _tokenIds, address _recipient) public {
    //...
    collectionToken_.burnFrom(msg.sender, tokenIdsLength * 1 ether * 10 ** collectionToken_.denomination());
    //..
}
```
So a user with a lot of NFT could thereby alter the total supply of ERC20 tokens, which in turn influences interest rates that used directly to calculate calculateCompoundedFactor
```solidity
function calculateCompoundedFactor(uint _previousCompoundedFactor, uint _utilizationRate, uint _timePeriod) public view returns (uint compoundedFactor_) {
    uint interestRate = this.calculateProtectedInterest(_utilizationRate);
    uint perSecondRate = (interestRate * 1e18) / (365 * 24 * 60 * 60);
    compoundedFactor_ = _previousCompoundedFactor * (1e18 + (perSecondRate / 1000 * _timePeriod)) / 1e18;
}
```
We use this to Calculate the amount of tax that would need to be paid against protected blob/main/flayer/src/contracts/ProtectedListings.sol#L607-L617 this function is used to check the protected listing health in getProtectedListingHealth that used in liquidateProtectedListing. An exploitation of the direct relation between the totalSupply and the liquidation is possible by a malicious user who owns half of the NFTs. The user can perform an action that causes the liquidation of the positions of the other participants and receives the KEEPER_REWARD for being a keeper for initiating the liquidation process. In addition, the user can buy up the one that had its NFT liquidated at an auction at a discount price which increases their gain. The impact of this vulnerability is that it allows a user to exploit the system to force protected listings into liquidation. This can lead to losses for other users whose listings are liquidated. It undermines the stability and fairness of the protocol by enabling manipulative tactics.

## Recommendation
use fees in deposit and redeem
