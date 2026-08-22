# [H] Staking Functionality is broken for approved addresses by owners of  the ERC20 tokens

## Summary
Severity: High
Chain: Smart contract
Component: Convergence---Convex-integration
Published: 2024-05-03
Source: https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/issues/50
Type: hats-finding

## Details
**Github username:** @0xumarkhatab
**Twitter username:** 0xumarkhatab
**Submission hash (on-chain):** 0x9e7d3e6658f64e6bac35f885204a474a01ef1278ef7397708688d284b003bbe1
**Severity:** high

**Description:**
**Description**\
Most functions inside the staking contracts requires the receiver or `msg.sender` to be the `strict owner` of the token they are using.
However , this functionality should also be available for `approved addresses ` of those token owners.

**Attack Scenario**\
Let's take a look at the following code snippets

stakingPositionService#deposit

```solidity
 function deposit(uint256 tokenId, uint256 cvgCvxAmount, DepositCvxData calldata cvxData) external {
        _deposit(tokenId, cvgCvxAmount, cvxData, false);
    }
    function _deposit(
        uint256 tokenId,
        uint256 cvgCvxAmount,
        DepositCvxData memory cvxData,
        bool isEthDeposit
    ) internal {
        // snip
        if (tokenId != 0) {
            /// @dev Fetches, for the tokenId, the owner, the StakingPositionService linked to and the timestamp of unlocking
            _cvxStakingPositionManager.checkIncreaseDepositCompliance(tokenId, msg.sender);
            _tokenId = tokenId;
        }
        // snip

        
    }
```

stakingServiceBase

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/issues/50_
