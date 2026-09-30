# [M] Possible Royalty OverCollection In sendFeesWithRoyalties()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 12567
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the Nested protocol has a FeeSplitter contract that is designed to receive fees collected by the NestedFactory, and split the income among shareholders, including the NFT owners, Nested treasury and a NST buybacker contract. The fee collection gives certain discount to so-called VIP accounts. Our analysis with the VIP accounts shows the current fee collection logic can be improved.
We use the same sendFeesWithRoyalties() function as an example. The VIP account is only validated within the sendFees() helper routine. However, the _royaltiesTarget share is collected without taking into account the VIP discount. The no-consideration of VIP discount may make the internal accounting inaccurate.
```solidity
/**
 * @dev Sends a fee to this contract for splitting, as an ERC20 token
 * @param _amount [uint256] amount of token as fee to be claimed by this contract
 * @param _royaltiesTarget [address] the account that can claim royalties
 * @param _token [IERC20] currency for the fee as an ERC20 token
 * @param _nftOwner [address] user owning the NFT and paying for the fees
 */
function sendFeesWithRoyalties(
    address _nftOwner,
    address _royaltiesTarget,
    IERC20 _token,
    uint256 _amount
) public {
    require(_royaltiesTarget != address(0), "FeeSplitter: INVALID_ROYALTIES_TARGET_ADDRESS");
    _addShares(_royaltiesTarget, _computeShareCount(_amount, royaltiesWeight, totalWeights), address(_token));
    _sendFees(_nftOwner, _token, _amount, totalWeights);
}

function _sendFees(
    address _nftOwner,
    IERC20 _token,
    uint256 _amount,
    uint256 _totalWeights
) private {
    // give a discount to VIP users
    if (_isVIP(_nftOwner)) _amount -= (_amount * vipDiscount) / 1000;
    IERC20(_token).safeTransferFrom(msg.sender, address(this), _amount);
    for (uint256 i = 0; i < shareholders.length; i++) {
        _addShares(
            shareholders[i].account,
            _computeShareCount(_amount, shareholders[i].weight, _totalWeights),
            address(_token)
        );
    }
    emit PaymentReceived(msg.sender, address(_token), _amount);
}
```

## Recommendation
Take into account the VIP status as well for the _royaltiesTarget share calculation.
