# [H] Liquidator receives less collateral then he should

## Summary
Severity: High
Contest weight: 0.7836
Dataset id: 19769
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Liquidator receives less collateral then he should
When VoltaVault.liquidateVault is called, then liquidator paysdebtofvault. Later, vault's collateral should be distributed among the liquidator and protocol.
ol#L389-L397
```solidity
uint256 collateralExtract = vaultCollateral[vaultID];
uint liquidatorDiscount = 100e18 * 1e18 / _minimumCollateralPercentage;
uint protocolFees = 1e18 - ((1e18 - liquidatorDiscount) / 2);
uint protocolEarned = collateralExtract * protocolFees / 1e18;
collateral.safeTransfer(treasury, protocolEarned);
vaultCollateral[vaultID] = 0;
collateral.safeTransfer(msg.sender, collateralExtract - protocolEarned);
```
According to the documentation:
For example, let's consider voltGNS with a minimum ratio of 150%, which is equivalent to a 66% Loan to Value ratio. If the LTV of voltGNS reaches 66%, it becomes eligible for liquidation. In this case, the liquidator would receive half of the 34% discount, or 17%, and the platform would receive the remaining 17% as fees. If the collateral is worth $1000, the liquidator would get it for $830, while the platform would receive $170 in fees.
The problem that in the code, it's protocol who receives $830 and liquidator receives only $170.
You can check it with this simple code in remix which uses code from protocol. Just run this in the remix and see result.
```solidity
contract Test {
    function test() external virtual pure returns (uint256, uint256) {
        uint256 collateralExtract = 100 ether;
        uint256 ratio = 150 ether;
        uint liquidatorDiscount = 100e18 * 1e18 / ratio;
        uint protocolFees = 1e18 - ((1e18 - liquidatorDiscount) / 2);
        uint protocolEarned = collateralExtract * protocolFees / 1e18;
        return (protocolEarned, collateralExtract - protocolEarned);
        //returns 83333333333333333300 for portocol and 16666666666666666700 for liquidator
        //so protocol receive more
    }
}
```
Liquidator lose big part of funds.

## Recommendation
Swap these amounts and send them to correct recipient.
