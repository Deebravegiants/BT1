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
    function adjustTrove(
        IStakeNTroveZap zapContract,
        address tm,
        uint256 mFee,
        uint256 wAmount,
        uint256 bAmount,
        bool isBorrowing
    ) public onlyManager nonReentrant {
        bytes32 positionId =
            registry.calculatePositionId(address(this), PRISMA_POSITION_ID, abi.encode(zapContract, tm));
        if (registry.getHoldingPositionIndex(vaultId, positionId, address(this), "") == 0) {
            revert IConnector_InvalidPosition(positionId);
        }
        IBorrowerOperations borrowerOps = zapContract.borrowerOps();
        if (bAmount > 0 && !isBorrowing) {
            _approveOperations(ITroveManager(tm).debtToken(), address(borrowerOps), bAmount);
        }
        borrowerOps.adjustTrove(tm, address(this), mFee, 0, wAmount, bAmount, isBorrowing, address(this), address(this));
        _updateTokenInRegistry(ITroveManager(tm).debtToken());
        // get health factor
>       uint256 healthFactor = ITroveManager(tm).getNominalICR(address(this));
>       if (minimumHealthFactor > healthFactor) {
>           revert IConnector_LowHealthFactor(healthFactor);
>       }
        emit AdjustTrove(address(zapContract), tm, mFee, wAmount, bAmount, isBorrowing);
    }
```

## Proof of Concept

N/A

## Tools Used

Manual review.

## Recommended Mitigation Steps

Copy the health factor code to `openTrove()` function.

```solidity
       uint256 healthFactor = ITroveManager(tm).getNominalICR(address(this));
       if (minimumHealthFactor > healthFactor) {
           revert IConnector_LowHealthFactor(healthFactor);
       }
```


## Assessed type

Other
