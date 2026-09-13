# [C] Re-entrancy issue for ERC1155

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

ERC1155 tokens have callback functions on some of the transfers, like `safeTransferFrom`, `safeBatchTransferFrom`. During these transfers, the `IERC1155ReceiverUpgradeable(to).onERC1155Received` function is called in the `to` address.

For example,  `safeTransferFrom`  is used in the `LiquidityMining` contract: 


**code/contracts/LiquidityMining.sol:L204-L224**
```solidity
function distributeAllNFT() external {
    require(block.timestamp > getEndLMTime(),
        "2 weeks after liquidity mining time has not expired");
    require(!isNFTDistributed, "NFT is already distributed");

    for (uint256 i = 0; i < leaderboard.length; i++) {
        address[] memory _groupLeaders = groupsLeaders[leaderboard[i]];

        for (uint256 j = 0; j < _groupLeaders.length; j++) {
            _sendNFT(j, _groupLeaders[j]);
        }
    }

    for (uint256 i = 0; i < topUsers.length; i++) {
        address _currentAddress = topUsers[i];
        LMNFT.safeTransferFrom(address(this), _currentAddress, 1, 1, "");
        emit NFTSent(_currentAddress, 1);
    }

    isNFTDistributed = true;
}
```
 
During that transfer, the `distributeAllNFT ` function can be called again and again. So multiple transfers will be done for each user.

In addition to that, any receiver of the tokens can revert the transfer. If that happens, nobody will be able to receive their tokens.

#### Recommendation

* Add a reentrancy guard. 
* Avoid transferring tokens for different receivers in a single transaction.
