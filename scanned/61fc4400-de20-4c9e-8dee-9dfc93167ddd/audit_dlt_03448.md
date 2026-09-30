# [M] `_getPositionTVL()` of The StargateConnector doesn't accoount for the total value locked.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1236
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/StargateConnector.sol#L114


# Vulnerability details

## Summary:
On the call to get the total value locked in a position in StargateConnector.sol, the value returned doesn't account for the full value in the position.
## Vulnerability Details:
When a token is deposited to Stargate in Line `54`, the LP tokens of the corresponding pool are deposited in the LPStaking contract in Line `63`, to gain  rewards in `STG` Tokens which is a means to maximize the yield generated for the funds deposited to the connector:
[StargateConnector.sol#L49-L70](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/StargateConnector.sol#L49C1-L70C6)
```solidity
49:    function depositIntoStargatePool(StargateRequest calldata depositRequest) external onlyManager nonReentrant {
50:        address lpAddress = LPStaking.poolInfo(depositRequest.poolId).lpToken;
51:        address underlyingToken = IStargatePool(lpAddress).token();
52:        if (depositRequest.routerAmount > 0) {
53:            _approveOperations(underlyingToken, address(stargateRouter), depositRequest.routerAmount);
54:            stargateRouter.addLiquidity(depositRequest.poolId, depositRequest.routerAmount, address(this));
55:            _updateTokenInRegistry(underlyingToken);
56:        }
57:        if (depositRequest.LPStakingAmount > 0) {
58:            uint256 stakingAmount = depositRequest.LPStakingAmount;
59:            if (depositRequest.LPStakingAmount == type(uint256).max) {
60:                stakingAmount = IERC20(lpAddress).balanceOf(address(this));
61:            }
62:            _approveOperations(lpAddress, address(LPStaking), stakingAmount);
63:            LPStaking.deposit(depositRequest.poolId, stakingAmount);
64:        }
65:        _updateTokenInRegistry(rewardToken);
66:        bytes32 positionId =
67:            registry.calculatePositionId(address(this), STARGATE_LP_POSITION_TYPE, abi.encode(depositRequest.poolId));
68:        registry.updateHoldingPosition(vaultId, positionId, "", "", false);
69:        emit DepositIntoStargatePool(depositRequest);
70:  }
```
The issue here is on the call to `_getPositionTVL()`, In Line `114` the only value accounted for is the LPToken & the amount staked into the LPstaking contract:

[StargateConnector.sol#L110-L121](https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/StargateConnector.sol#L110C1-L121C6)
```solidity
110:   function _getPositionTVL(HoldingPI memory p, address base) public view override returns (uint256 tvl) {
111:        PositionBP memory pBP = registry.getPositionBP(vaultId, p.positionId);
112:        uint256 poolId = abi.decode(pBP.data, (uint256));
113:        address lpAddress = LPStaking.poolInfo(poolId).lpToken;
114:        uint256 lpAmount = LPStaking.userInfo(poolId, address(this)).amount + IERC20(lpAddress).balanceOf(address(this));
115:        if (lpAmount == 0) {
116:            return 0;
117:        }
118:        address underlyingToken = IStargatePool(lpAddress).token();
119:        uint256 underlyingAmount = IStargatePool(lpAddress).amountLPtoLD(lpAmount);
120:        return _getValue(underlyingToken, base, underlyingAmount);
121:    }
```
However, it doesn't account for the `LPStaking.userInfo.rewardDebt` which is the yield gained in STG Tokens for staking in the LPstaking contract, this will cause the `_getPositionTVL()` to reflect a lower `TVL` that it actually has.
## Impact:
The rewards might be seen as small, however, over time as the rewards grow bigger this will not be accounted for in the `TVL` allowing shares to be distributed incorrectly. 
## Recommended Mitigation Details:
account for the STG Tokens gotten as yield/rewards for staking the LP tokens by getting the value from the `LPStaking.userInfo` and converting to get the value in the base amount.


## Assessed type

Context
