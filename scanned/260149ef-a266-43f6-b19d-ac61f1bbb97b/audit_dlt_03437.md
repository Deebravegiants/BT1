# [M] `totalAssets()`, and thus `convertToShares()` and `convertToAssets()`, may revert, in violation of ERC-4626

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1329
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/valueOracle/NoyaValueOracle.sol#L107


# Vulnerability details




## Impact
`totalAssets()` may revert, which in turn causes `convertToShares()` and `convertToAssets()` to revert, each possibility of revert of which is a violation ERC-4626.

## Proof of Concept
[AccountingManager is to be ERC-4626 compliant](https://github.com/code-423n4/2024-04-noya?tab=readme-ov-file#:~:text=src/accountingManager/AccountingManager,ERC4626). Therefore [`totalAssets()` MUST NOT revert](https://eips.ethereum.org/EIPS/eip-4626#:~:text=in%20the%20Vault.-,MUST%20NOT%20revert.,-%2D%20name%3A).

However, `AccountingManager.totalAssets()` [returns `TVL()`](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L592) which [returns a sum including `TVLHelper.getTVL()`](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L628) which [calls `IConnector.getPositionTVL()`](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/TVLHelper.sol#L22) on the connector of every position. In all connectors this calls `NoyaValueOracle._getValue()` which [explicitly may revert](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/valueOracle/NoyaValueOracle.sol#L107) if an oracle is unavailable. `AccountingManager.totalAssets()` may thus revert.

This then also causes `convertToShares()` and `convertToAssets()`, which make use of `totalAssets()` to revert.

## Recommended Mitigation Steps
Consider returning `0` instead of reverting. If an oracle is unavailable it seems reasonable to consider this asset temporarily worthless. This might cause a price drop in `totalAssets()` instead of reverting. Consider what the implications of this could be, if any. If necessary consider perhaps using the last known value as an "oracle" of last resort instead of reverting.


## Assessed type

ERC4626
