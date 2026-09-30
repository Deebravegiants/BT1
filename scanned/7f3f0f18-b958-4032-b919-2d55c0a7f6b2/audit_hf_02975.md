# [M] Incomplete Validation

## Summary
Severity: Medium
Contest weight: 0.4939
Dataset id: 16526
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the NFTVesting.sol contract the following validation checks are missing:
- In constructor() if _startTime is set in the past the getTimePassed() function will revert on every call and there claim() will be unusable. The same applies for _vestingPeriod and _tokenAmount to be greater than 0.
- In claim() function check whether the vesting period has started and whether the vesting period has ended. A zero-value check for claimable should be applied as well.

In the Stake.sol contract the following validation checks are missing:
- stake() and startUnstake() functions are missing zero-value checks.

In the OnlyYeetContract.sol contract the following validation checks are missing:
- setYeetContract() function missing zero address check for _yeetContract parameter.

In the Reward.sol contract the following validation checks are missing:
- addYeetVolume() function missing zero address check for user parameter.
- In the addYeetVolume() function there is a require statement which must not allow zero amount to be sent for the tx but the comparison allows zero value to pass.

In the Yeet.sol contract the following validation checks are missing:
- constructor() missing zero address check for _publicGoodsAddress, _lpStakingAddress and _teamAddress.
- restart() function missing empty bytes check for userRandomNumber parameter.
- setPublicGoodsAddress(), setLpStakingAddress(), setTreasuryRevenueAddress(), setYeetardsNFTsAddress() functions are missing zero address checks.

In the Yeetback.sol contract the following validation checks are missing:
- constructor() missing zero address check for _entropy and _entropyProvider parameters.
- addYeetsInRound() function missing zero-value check for round and zero address check for user parameters.
- addYeetback() function missing empty bytes check for userRandomNumber and zero-value checks for round and amount parameters.
- claim() function zero-value check for the round parameter.

## Recommendation
Implement the following validation checks:
```solidity
// File: NFTVesting.sol
constructor(
    IERC20 _token,
    INFTContract _nftContract,
    uint256 _tokenAmount,
    uint256 _nftAmount,
    uint256 _startTime,
    uint256 _vestingPeriod
) {
    require(_startTime >= block.timestamp, "NFTVesting: startTime should be in the future");
    require(_vestingPeriod != 0, "NFTVesting: vestingPeriod should be larger than 0");
    require(_tokenAmount != 0, "NFTVesting: _tokenAmount should be larger than 0");
}

function claim(uint256 tokenId) public {
    require(claimable != 0, "Nothing to claim");
}

// File: Stake.sol
function stake(uint256 amount) external {
    require(amount != 0, "Invalid stake amount");
}

function startUnstake(uint256 unStakeAmount) external {
    require(unStakeAmount != 0, "Invalid unstake amount");
}

// File: OnlyYeetContract.sol
function setYeetContract(address _yeetContract) external onlyOwner {
    require(_yeetContract != address(0), "Invalid yeet contract address");
}

// File: Reward.sol
function addYeetVolume(address user, uint256 amount) external onlyYeetOwner {
    require(amount != 0, "Amount must be greater than 0");
    require(user != address(0), "Invalid user address");
}

// File: Yeet.sol
constructor(
    YeetToken _token,
    Reward _reward,
    DiscreteStakingRewards _staking,
    YeetGameSettings _gameSettings,
    address _publicGoodsAddress,
    address _lpStakingAddress,
    address _teamAddress
) Pauseable(msg.sender) {
    require(_publicGoodsAddress != address(0), "Invalid public goods address");
    require(_lpStakingAddress != address(0), "Invalid lp staking address");
    require(_teamAddress != address(0), "Invalid team address");
}

function restart(bytes32 userRandomNumber) payable external whenNotPaused {
    require(userRandomNumber != bytes32(0), "Invalid number");
}

function setPublicGoodsAddress(address _publicGoodsAddress) external onlyOwner {
    require(_publicGoodsAddress != address(0), "Invalid public goods address");
}

function setLpStakingAddress(address _lpStakingAddress) external onlyOwner {
    require(_lpStakingAddress != address(0), "Invalid lp staking address");
}

function setTreasuryRevenueAddress(address _treasuryRevenueAddress) external onlyOwner {
    require(_treasuryRevenueAddress != address(0), "Invalid treasury revenue address");
}

function setYeetardsNFTsAddress(address _yeetardsNFTsAddress) external onlyOwner {
    require(_yeetardsNFTsAddress != address(0), "Invalid NFTs contract address");
}

// File: Yeetback.sol
constructor(address _entropy, address _entropyProvider) Ownable(msg.sender) {
    require(_entropy != address(0), "Invalid entropy address");
    require(_entropyProvider != address(0), "Invalid entropy provider address");
}

function addYeetsInRound(uint256 round, address user) public onlyOwner {
    require(round != 0, "Invalid round");
    require(user != address(0), "Invalid user address");
}

function addYeetback(bytes32 userRandomNumber, uint256 round, uint256 amount) payable public onlyOwner {
    require(userRandomNumber != bytes32(0), "Invalid number");
    require(round != 0, "Invalid round");
    require(amount != 0, "Invalid amount");
}

function claim(uint256 round) public {
    require(round != 0, "Invalid round");
}
```
