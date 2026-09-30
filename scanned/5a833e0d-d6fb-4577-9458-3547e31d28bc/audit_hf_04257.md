# [H] `PrismaConnector` can mint a position below the desired health factor

## Summary
Severity: High
Contest weight: 0.9634
Dataset id: 21202
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
[PrismaConnector::adjustTrove](https://github.com/georgiIvanov/noya-audit/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/PrismaConnector.sol#L117-L120)

The `PrismaConnector` contract is responsible for minting ULTRA and managing the collateral backing it. When a trove is opened, collateral is put up and ULTRA minted to the `PrismaConnector`. The contract also allows to manage how much of the stablecoin is minted or repay some of it, to improve the collateral ratio (CR). Since collateral can be liquidated an additional check is made to ensure adjustment operations don’t leave the trove insolvent:
    
    uint256 healthFactor = ITroveManager(tm).getNominalICR(address(this);
    if (minimumHealthFactor > healthFactor) {
        revert IConnector_LowHealthFactor(healthFactor);
    }

The issue lies in the fact that `getNominalICR` is used to get the health factor (aka CR) and the resulting value is always less than `minimumHealthFactor` (1.5e18). Unless an unreasonable amount of collateral is put up. Thus, `adjustTrove` becomes practically unusable to borrow or repay.
```

## Proof of Concept
```solidity
The following test demonstrates how adjusting the trove fails once it’s opened.

Keep in mind that the only part that fails is the wrongly checked CR, actual interaction with Prisma works. Which means that the trove has enough collateral to adjust.

In `ITroveManager` add the following method:
    
    function getCurrentICR(address _borrower, uint256 _price) external view returns (uint256);

In `PrismaConnector.t.sol` add the following test and run with `forge test --mt testTroveHealthFactor -vvv`:
    
    function testTroveHealthFactor() public {
        uint256 amount = 2e18;                   // collateral
        uint256 ultraToMint = 2000e18;
        _dealERC20(WETH, address(connector), amount);
    
        uint256 wethPrice = chainlinkOracle.getValue(address(WETH), address(840), 1 ether);
        console.log("wethPrice   :", wethPrice); // 3037$ per WETH
    
        vm.startPrank(owner);
    
        connector.approveZap(IStakeNTroveZap(ULTRA_StakeNTroveZap), ULTRA_weeth_troveManager, true);
        connector.openTrove(
            IStakeNTroveZap(ULTRA_StakeNTroveZap), ULTRA_weeth_troveManager, 
            125e14,     // max fee
            amount,     // collateral
            ultraToMint // ULTRA to mint
        );
    
        ITroveManager tm = ITroveManager(ULTRA_weeth_troveManager);
        (uint256 coll1, uint256 debt1) = tm.getTroveCollAndDebt(address(connector));
        console.log("coll1       :", coll1);
        console.log("debt1       :", debt1);
        console.log("minHF       :", connector.minimumHealthFactor()); // 1.5
        
        uint256 connectorMinHF = connector.minimumHealthFactor();
        uint256 troveHF = tm.getCurrentICR(address(connector), wethPrice * 1e10);  // or coll1 * (wethPrice * 1e10) / debt1;
        console.log("troveHF     :", troveHF);
    
        assertGt(troveHF, connector.minimumHealthFactor()); // 2000 ULTRA is backed up by 2 WETH, so troveHF is well above 1.5
    
        // Next call fails, when it shouldn't; health factor of the trove is above connector.minimumHealthFactor()
        vm.expectRevert();
        // repay 1 ULTRA
        connector.adjustTrove( 
            IStakeNTroveZap(ULTRA_StakeNTroveZap), 
            ULTRA_weeth_troveManager, 
            125e14, // max fee
            0,      // collateral to withdraw
            1e18,   // repay amount
            false   // is repay 
        );
    
        // There should be enough collateral to borrow 1 ULTRA, but call fails
        vm.expectRevert();
        // borrow 1 ULTRA
        connector.adjustTrove( 
            IStakeNTroveZap(ULTRA_StakeNTroveZap), 
            ULTRA_weeth_troveManager, 
            125e14, // max fee
            0,      // collateral to withdraw
            1e18,   // borrow amount
            true   // is borrow 
        );
    }
```

## Recommendation
```solidity
Check the price for one unit of the collateral token using `valueOracle`. Then, call `troveManager.getCurrentICR(address(this), collateralPrice)` to get the actual CR and compare it to the minimum.
    
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
            uint256 collateralPrice = _getValue(ITroveManager(tm).collateralToken(), ChainlinkOracleConnector.USD(), 1);
            uint256 healthFactor = ITroveManager(tm).getCurrentICR(address(this), collateralPrice);
            if (minimumHealthFactor > healthFactor) {
                revert IConnector_LowHealthFactor(healthFactor);
            }
            emit AdjustTrove(address(zapContract), tm, mFee, wAmount, bAmount, isBorrowing);
        }

If ULTRA is repaid - don’t revert if the collateral ratio is below minimum. This will allow repaying ULTRA even when below threshold, which will enable the protocol to repay the debt even in the edge case where Prisma CR is ok, but connectors’ CR is below minimum.

In `ITroveManager` add the following two functions:
    
    function getCurrentICR(address _borrower, uint256 _price) external view returns (uint256);
        
    function collateralToken() external view returns (address);
```
