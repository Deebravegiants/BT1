# [M] `PrismaConnector.sol` should also check health factor in `openTrove()` function

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1128
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/PrismaConnector.sol#L52-L67


# Vulnerability details


## Bug Description

`PrismaConnector.sol` does not check health factor in `openTrove()` function. Though this function is the initialization phase of a Trove account, it still supports both adding collateral and borrowing, so the health factor should be checked, just like in `adjustTrove()` function.

```solidity
    /**
     * @notice Opens a new trove with specified parameters using the zap contract
     * @param zap The address of the StakeNTroveZap contract used for interaction
     * @param tm The address of the TroveManager contract
     * @param maxFee Maximum fee for the operation
     * @param dAmount The amount of collateral to deposit
     * @param bAmount The amount of borrowing
     */
    function openTrove(IStakeNTroveZap zap, address tm, uint256 maxFee, uint256 dAmount, uint256 bAmount)
        public
        onlyManager
        nonReentrant
    {
        bytes32 positionId = registry.calculatePositionId(address(this), PRISMA_POSITION_ID, abi.encode(zap, tm));
        PositionBP memory positionInfo = registry.getPositionBP(vaultId, positionId);
        address collateral = abi.decode(positionInfo.additionalData, (address));
        address debTtoken = ITroveManager(tm).debtToken();
        _approveOperations(collateral, address(zap), dAmount);
        zap.openTrove(tm, maxFee, dAmount, bAmount, address(this), address(this));
        registry.updateHoldingPosition(vaultId, positionId, "", "", false);
        _updateTokenInRegistry(collateral);
        _updateTokenInRegistry(debTtoken);
        emit OpenTrove(address(zap), tm, maxFee, dAmount, bAmount);
    }
    ...
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1128_
