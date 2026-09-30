# [M] During Recovery Mode Liquidation, the

## Summary
Severity: Medium
Contest weight: 0.7640
Dataset id: 2643
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidation in recovery mode, protocol implements separate tracking of Total Collateral Ratio (TCR) (see line 350 and 526 below) which is incorrectly calculated because the entireSystemColl value has a missing subtraction of collateral gas compensation that lead to inaccuracy of computation. This will inflate the value of TCR and affects both liquidateDens and batchLiquidateDens File: LiquidationManager.sol 337: entireSystemColl -= totals.totalCollToSendToSP * ~ continue 350: uint256 TCR = here is inflated ,→ ,→ ~ continue 364: entireSystemColl -= 365: (singleLiquidation.collToSendToSP + compensation ,→ ,→ 366: denManagerValues.price; File: LiquidationManager.sol 503: entireSystemColl -= totals.totalCollToSendToSP * ~ continue 526: uint256 TCR = here is inflated ,→ ,→ ~continue 541: entireSystemColl -= 542: (singleLiquidation.collToSendToSP + compensation ,→ ,→ 543: denManagerValues.price; entireSystemColl is supposed to track the total system collateral during liquidations. While it correctly deducts the collateral sent to the Stability Pool and the surplus collateral amount, it fails to account for the collateral gas compensation. The collateral gas compensation is necessary to deduct so the system can compute the real value of TCR. Remember that collateral gas compensation is being sent as reward for liquidators, snect gauge and validator pool, in which being deducted from actual system collateral. If we don't deduct it, the TCR is inflated, that will affect the liquidation of dens, like for example, that a den should be liquidated but due to inflated TCR, it will become higher than CCR, therefore no liquidation. The root cause can be trace in a situation where the system's TCR falls below the Critical Collateralization Ratio (CCR), triggering recovery mode in which proper liquidation will apply. The bug arises here because the TCR is inflated as collateral gas compensation is not deducted from the system's collateral. The issue is present in both liquidateDens and batchLiquidateDens Internal Pre-conditions External Pre-conditions Attack Path See POC section for vulnerability path. TCR is artificially inflated, it means calculated TCR during liquidation is higher than actual. It means that Dens higher than actual TCR will be wrongly liquidated. Another case is that liquidation should happen but won't because the TCR is inflated in which it becomes higher than CCR. Therefore no liquidation happened.

## Proof of Concept
Please follow first the instruction here in the secret gist link before running the test. 1. Insert this test under this file blockend/test/core/LiquidationManager.t.sol
```solidity
function test_liquidateDensTCRDiff() external {
    _openDenA(depositor); // Open DenA with 185% ICR
    _openDenB(random);// Open DenB with 250% ICR
    _openDenC(depositor2);// Open DenC 221% ICR
    // After 12 seconds
    vm.warp(block.timestamp + 12 seconds);
    // Enable recovery mode, price drops to 60% of initial price
    _mockPriceFeed(6e17, block.timestamp, 2);
    // LiquidateDens
    vm.prank(addrs.factory);
    vm.recordLogs();
    liquidationManager.liquidateDens(denManager, 2, MCR, addrs.factory);
    VmSafe.Log[] memory logss = vm.getRecordedLogs();
    uint256 finalTCR = borrowerOperations.getTCR();
    (uint256 postColl, uint256 postDebt) = borrowerOperations.getGlobalSystemBalances();
    console.log("\nAfter-liquidation:");
    // Parse TCR events and verify difference
    for (uint i = 0; i < logss.length; i++) {
        if (logss[i].topics[0] == keccak256("TCRCalculated(uint256,uint256,uint256)")) {
            (uint256 calculatedTCR, uint256 usedColl, uint256 usedDebt) = abi.decode(logss[i].data, (uint256,uint256,uint256));
            console.log("Used Collateral in calculation:", usedColl);
            console.log("Used Debt in calculation:", usedDebt);
            console.log("Calculated TCR:", calculatedTCR);
            console.log("TCR Difference:", calculatedTCR - finalTCR);
        }
    }
}
```
2. Run the test forge test -vv --match-contract LiquidationManagerTest --match-test test_liquidateDensTCRDiff TCR and Calculated TCR. This represents the unaccounted subtraction of collateral compensated gas. After-liquidation: Used Collateral in calculation: 2880000000000000000000000000000000000 Used Debt in calculation: 2237130008512671232 Calculated TCR: 1287363715582507915 TCR Difference: 2145606192637513 Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 188.06s (5.35s CPU time)

## Recommendation
Deduct collateral gas compensation when maintaining entireSystemColl.
```solidity
entireSystemColl -= totals.totalCollToSendToSP * denManagerValues.price;
```
```solidity
entireSystemColl -= (totals.totalCollGasCompensation + totals.totalCollToSendToSP) * denManagerValues.price;
```
```solidity
entireSystemColl -= (singleLiquidation.collToSendToSP + singleLiquidation.collSurplus) * denManagerValues.price;
```
```solidity
entireSystemColl -= (singleLiquidation.collToSendToSP + singleLiquidation.collSurplus + singleLiquidation.collGasCompensation) * denManagerValues.price;
```
