# [H] Improper Design For ThemisEarlyFarmingNFT(ERC721) Transfer

## Summary
Severity: High
Contest weight: 0.6376
Dataset id: 13245
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Themis V3 protocol, the ThemisEarlyFarming contract implements a term deposit mechanism. With that, the user can not only earn lending interests on his deposits, but also get bonus rewardToken. Additionally, the ThemisEarlyFarmingNFT contract implements the ERC721 standard to identify each deposit through the ThemisEarlyFarming contract. In other words, each deposit is treated as a NFT and its related information is stored in the earlyFarmingNftInfos and userNftPeriodPoolIdAllTokenIds mapping (lines 27/29) of the ThemisEarlyFarmingNFT contract. In particular, one ERC721 standard interface, i.e., safeTransferFrom(), is overridden to support NFT transfer with its related deposit information update. While examining the logic of it, we notice there is an improper implementation that needs to be improved.
To elaborate, we show below the related code snippet of the ThemisEarlyFarming and ThemisEarlyFarmingNFT contracts. In the overridden safeTransferFrom() function of the ThemisEarlyFarmingNFT contract, the internal _updateNftInfo() function is called (line 169) to update the NFT related deposit information. However, it ignores the fact that the userPeriodInfos mapping of the ThemisEarlyFarming contract also stores the deposit information. The calling of safeTransferFrom() will introduce unexpected state inconsistencies between the ThemisEarlyFarming and ThemisEarlyFarmingNFT contracts, which may result withdrawal failure for the NFT corresponding deposit.
Public
Moreover, note that the lending interests and bonus rewardToken will be transferred to the new owner with the NFT transfer.
```solidity
contract ThemisEarlyFarmingNFT is IThemisEarlyFarmingNFTStorage, ERC721, ERC721Enumerable, Governance {
    using Counters for Counters.Counter;
    using SafeMath for uint256;
    using EnumerableSet for EnumerableSet.UintSet;
    event WithdarwAmountsEvent(address indexed sender, WtihdrawNftParams wtihdrawNftParams);
    Counters.Counter private _tokenIdCounter;
    address public miner;
    address public themisEarlyFarmingNFTDescriptor;
    mapping(uint256 => EarlyFarmingNftInfo) public earlyFarmingNftInfos;
    mapping(address => mapping(uint256 => EnumerableSet.UintSet)) userNftPeriodPoolIdAllTokenIds; // user address => periodPoolId => periodPoolId set // all records
    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory _data
    ) public virtual override(ERC721) {
        require(_isApprovedOrOwner(_msgSender(), tokenId), "ERC721: transfer caller is not owner nor approved");
        _updateNftInfo(tokenId, to);
        super._safeTransfer(from, to, tokenId, _data);
    }
    function _updateNftInfo(uint256 tokenId, address to) internal {
        EarlyFarmingNftInfo storage nftInfo = earlyFarmingNftInfos[tokenId];
        address nftOnwer = nftInfo.onwerUser;
        userNftPeriodPoolIdAllTokenIds[nftOnwer][nftInfo.periodPoolId].remove(tokenId);
        nftInfo.onwerUser = to;
        userNftPeriodPoolIdAllTokenIds[to][nftInfo.periodPoolId].add(tokenId);
    }
}
function userDeposit(uint256 _periodPoolId, uint256 _amount) external checkPeriodVaild(_periodPoolId) {
    require(_amount > 0, "deposit input invalid amount.");
    public address _user = msg.sender;
    _settlementProfit(_periodPoolId);
    uint256 _currBlock = block.number;
    PeriodPool storage _periodPool = periodPools[_periodPoolId];
    address _token = _periodPool.token;
    // update gobal
    tokenCurrTotalDeposit[_token] = tokenCurrTotalDeposit[_token].add(_amount);
    // update period
    _periodPool.currTotalDeposit = _periodPool.currTotalDeposit.add(_amount);
    // update user
    UserPeriodInfo storage _userPeriodInfo = userPeriodInfos[_periodPoolId][_user];
    _userPeriodInfo.currDeposit = _userPeriodInfo.currDeposit.add(_amount);
    IERC20(_token).safeTransferFrom(_user, address(this), _amount);
    IERC20(_token).safeApprove(address(themisLendCompound), _amount);
    themisLendCompound.userLend(_periodPool.lendPoolId, _amount);
    // send user a NFT
    EarlyFarmingNftInfo memory _nftInfo = EarlyFarmingNftInfo({
        periodPoolId: _periodPoolId,
        buyUser: _user,
        onwerUser: _user,
        pledgeToken: _token,
        pledgeAmount: _amount,
        withdrawAmount: 0,
        lastUnlockBlock: _currBlock,
        startBlock: _currBlock,
        endBlock: _currBlock + _periodPool.periodBlock,
        buyTime: block.timestamp,
        perBlockUnlockAmount: 0,
        lastInterestsShare: _periodPool.interestsShare,
        lastRewardsShare: _periodPool.rewardsShare
    });
    themisEarlyFarmingNFT.safeMint(_user, _nftInfo);
    emit UserDepositEvent(_user, _periodPoolId, _amount);
```

## Recommendation
Correct the implementation of the safeTransferFrom() routine to keep state consistency between the ThemisEarlyFarming and ThemisEarlyFarmingNFT contracts.
