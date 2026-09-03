# [M] The `TVLHelper.sol#getTVL` function is DOSed by the `under collateralized connector`, and as a result, many parts of the protocol may be DOS.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1286
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/main/contracts/accountingManager/AccountingManager.sol#L1-L708
https://github.com/code-423n4/2024-04-noya/blob/main/contracts/helpers/TVLHelper.sol#L1-L54
https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/AaveConnector.sol#L1-L123
https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/CompoundConnector.sol#L1-L144
https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/Dolomite.sol#L1-L123
https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/PrismaConnector.sol#L1-L174
https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/SiloConnector.sol#L1-L149


# Vulnerability details

## Impact
Many functions of the protocol may be DOS.

## Proof of Concept
If `connectors` are under collateralized, the `_getPositionTVL` function may be reverted.
For example, the `AaveConnector.sol#_getPositionTVL` function is as follows.
The `AccountingManager.sol#executeWithdraw`function is as follows.
```solidity
    function _getPositionTVL(HoldingPI memory, address base) public view override returns (uint256 tvl) {
        (uint256 totalCollateralBase, uint256 totalDebtBase,,,,) = IPool(pool).getUserAccountData(address(this));
116:    uint256 poolBaseAmount = totalCollateralBase - totalDebtBase;
        return valueOracle.getValue(poolBaseToken, base, poolBaseAmount);
    }
```
As shown in `L116`, if `totalCollateralBase < totalDebtBase`, it is reverted.
The `TVLHelper.sol#getTVL`function is as follows.
```solidity
    function getTVL(uint256 vaultId, PositionRegistry registry, address baseToken) public view returns (uint256) {
        uint256 totalTVL;
        uint256 totalDebt;
        HoldingPI[] memory positions = registry.getHoldingPositions(vaultId);
        for (uint256 i = 0; i < positions.length; i++) {
            if (positions[i].calculatorConnector == address(0)) {
                continue;
            }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1286_
