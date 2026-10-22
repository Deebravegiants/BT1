# [M] Lack of function to claim reward in `AaveConnector`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1321
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/AaveConnector.sol#L11


# Vulnerability details

## Vulnerability details
From [aave docs](https://docs.aave.com/developers/periphery-contracts/rewardscontroller#claimrewards), function `claimrewards()` is used to claim reward when user have a/s/vtoken:

    function claimRewards(
        address[] calldata assets,
        uint256 amount,
        address to,
        address reward
    ) external override returns (uint256) {
        require(to != address(0), 'INVALID_TO_ADDRESS');
        return _claimRewards(assets, amount, msg.sender, msg.sender, to, reward);
  }
When supply token, user can receive atokens [link](https://github.com/aave/aave-v3-core/blob/724a9ef43adf139437ba87dcbab63462394d4601/contracts/interfaces/IPool.sol#L248), but because these is no mechanism to claim these reward, they are being stuck in the aave.

## Impact
There is no way to claim reward that generated when supply token

## Tools Used
Manual review

## Recommended Mitigation Steps
Add function to claim reward by calling `claimReward()` function in aave.


## Assessed type

Context
