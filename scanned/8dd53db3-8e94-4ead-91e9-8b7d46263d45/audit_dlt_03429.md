# [M] Missing calls to `_updateTokenInRegistry` leads to incorrect state of tokens in registry

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1404
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CurveConnector.sol#L212
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MaverickConnector.sol#L137
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/GearBoxV3.sol#L62
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MorphoBlueConnector.sol#L58
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/PrismaConnector.sol#L75
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/BalancerConnector.sol#L64


# Vulnerability details

## Impact
If the _updateTokenInRegistry() function is not called when it should be, the registry may not accurately reflect the current balances of tokens in the connectors leading to incorrect state.

## Proof of Concept
[_updateTokenInRegistry()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/BaseConnector.sol#L135) is called in different connector contracts functions. The purpose of this function is to update the token registry to reflect the current balance of a specified token. It can add a new token to the registry or remove a token with zero balance.

```js
 function _updateTokenInRegistry(address token, bool remove) internal {
        (address accountingManager,) = registry.getVaultAddresses(vaultId);
        // the value function is inside the accounting manager contract (so we can use the accounting manager address as the calculator connector)
        bytes32 positionId = registry.calculatePositionId(accountingManager, 0, abi.encode(token));
        // if the token is not in the registry, we add it or remove it if the remove flag is true
        uint256 positionIndex =
            registry.getHoldingPositionIndex(vaultId, positionId, address(this), abi.encode(address(this)));
        if ((positionIndex == 0 && !remove) || (positionIndex > 0 && remove)) {
            emit UpdateTokenInRegistry(token, remove);
            registry.updateHoldingPosition(vaultId, positionId, abi.encode(address(this)), "", remove);
        }
    }
```

According to protocol docs:
  > This function is called to ensure the registry is accurate after liquidity is added, removed, or swaps are performed. It should reflect the current state of tokens held by this connector.

But such calls are MISSING in various functions of different connectors where liquidity is either added or removed. 

[CurveConnector.sol::withdrawFromPrisma](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CurveConnector.sol#L212)
```js
  function withdrawFromPrisma(address depostiToken, uint256 amount) public onlyManager {
        IDepositToken(depostiToken).withdraw(address(this), amount); //@missing
        emit WithdrawFromPrisma(depostiToken, amount);
    }
```
[MaverickConnector.sol::claimBoostedPositionRewards](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MaverickConnector.sol#L137)
```js

    function claimBoostedPositionRewards(IMaverickReward rewardContract) external onlyManager nonReentrant { 
        IMaverickReward.EarnedInfo[] memory earnedInfo = rewardContract.earned(address(this));
        uint8 tokenIndex;
        for (uint256 i = 0; i < earnedInfo.length; i++) {
            if (earnedInfo[i].earned != 0) {
                tokenIndex = rewardContract.tokenIndex(address(earnedInfo[i].rewardToken));
                rewardContract.getReward(address(this), tokenIndex);
            }
        }
        emit ClaimBoostedPositionRewards(rewardContract);
    }

```

[GearBoxV3.sol:::executeCommands](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/GearBoxV3.sol#L62)
```js
function executeCommands(
        address facade,
        address creditAccount,
        MultiCall[] calldata calls,
        address approvalToken,
        uint256 amount
    ) public onlyManager nonReentrant {
        for (uint256 i = 0; i < calls.length; i++) {
            if (calls[i].target != facade) revert IConnector_InvalidTarget(calls[i].target);
            bytes4 method = bytes4(calls[i].callData[:4]);

            if (method == ICreditFacadeV3Multicall.enableToken.selector) {
                (address token) = abi.decode(calls[i].callData[4:], (address));
                _updateTokenInRegistry(token);
            }
        }
        if (approvalToken != address(0)) {
            _approveOperations(approvalToken, ICreditFacadeV3(facade).creditManager(), amount); //@missing
        }
        ICreditFacadeV3(facade).multicall(creditAccount, calls);
        if (approvalToken != address(0)) {
            _revokeApproval(approvalToken, ICreditFacadeV3(facade).creditManager());
        }
        emit ExecuteCommands(facade, creditAccount, calls, approvalToken, amount);
    }
```
[MorphoBlueConnector.sol::withdraw](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MorphoBlueConnector.sol#L58): either of the tokens should be updated inside if block
```js
function withdraw(uint256 amount, Id id, bool sOrC) external onlyManager nonReentrant {
        MarketParams memory params = morphoBlue.idToMarketParams(id);
        if (sOrC) {
            morphoBlue.withdraw(params, amount, 0, address(this), address(this));
        } else {
            morphoBlue.withdrawCollateral(params, amount, address(this), address(this));
        }
        Position memory p = morphoBlue.position(id, address(this));
        if (p.collateral == 0 && p.supplyShares == 0) {
            registry.updateHoldingPosition(
                vaultId, registry.calculatePositionId(address(this), MORPHO_POSITION_ID, abi.encode(id)), "", "", true
            );
        }
        _updateTokenInRegistry(params.collateralToken);
        emit Withdraw(amount, id, sOrC);
```

[PrismaConnector.sol::addColl](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/PrismaConnector.sol#L75)
```js
function addColl(IStakeNTroveZap zapContract, address tm, uint256 amountIn) public onlyManager nonReentrant { //@missing
        bytes32 positionId =
            registry.calculatePositionId(address(this), PRISMA_POSITION_ID, abi.encode(zapContract, tm));
        PositionBP memory positionInfo = registry.getPositionBP(vaultId, positionId);
        if (registry.getHoldingPositionIndex(vaultId, positionId, address(this), "") == 0) {
            revert IConnector_InvalidPosition(positionId);
        }
        address collateral = abi.decode(positionInfo.additionalData, (address));
        _approveOperations(collateral, address(zapContract), amountIn);
        zapContract.addColl(tm, amountIn, address(this), address(this));
        emit AddColl(address(zapContract), tm, amountIn);
    }
```

[BalancerConnector.sol::openPosition](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/BalancerConnector.sol#L64)
```js
function openPosition(
        bytes32 poolId,
        uint256[] memory amounts,
        uint256[] memory amountsWithoutBPT,
        uint256 minBPT,
        uint256 auraAmount
    ) public onlyManager nonReentrant {
        address[] memory tokens;
        {
            (tokens,,) = IBalancerVault(balancerVault).getPoolTokens(poolId);
        }
        address pool = IBalancerVault(balancerVault).getPool(poolId);

        for (uint256 i = 0; i < tokens.length; i++) {
            if (amounts[i] > 0) _approveOperations(tokens[i], balancerVault, amounts[i]);
        }

        IBalancerVault(balancerVault).joinPool(
            poolId,
            address(this), // sender
            address(this), // recipient
            IBalancerVault.JoinPoolRequest(
                tokens,
                amounts,
                abi.encode(
                    IBalancerVault.JoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT,
                    amountsWithoutBPT, //_noBptAmounts,
                    minBPT // minimumBPT
                ),
                false
            )
        );
        bytes32 positionId = registry.calculatePositionId(address(this), BALANCER_LP_POSITION, abi.encode(poolId));
        registry.updateHoldingPosition(vaultId, positionId, "", "", false);

        if (auraAmount > 0) {
            (PoolInfo memory _poolInfo,) = _getPoolInfo(poolId);

            uint256 amount = IERC20(pool).balanceOf(address(this));
            _approveOperations(pool, _poolInfo.auraPoolAddress, amount);
            IRewardPool(_poolInfo.auraPoolAddress).deposit(auraAmount, address(this));
        }
        emit OpenPosition(poolId, amounts, amountsWithoutBPT, minBPT, auraAmount);
    }
```
## Tools Used
Manual Review

## Recommended Mitigation Steps
Ensure that the `_updateTokenInRegistry()` function is called in all necessary places in the connector contracts. This function should be invoked whenever a token’s balance changes due to operations such as adding or removing liquidity, or performing swaps.


## Assessed type

Other
