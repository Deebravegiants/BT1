# [H] 5.2.2 Two differentinvariantCheckvariables used inPoolFactory.deployPool()

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** PoolFactory.sol#L93-L174, IPoolFactory.sol#L

**Description:** ThedeployPool()function in thePoolFactorycontract uses two differentinvariantCheckvari-
ables: the one defined as a contract’s instance variable and the one supplied as a parameter.

Note: This was also documented in Secureum’s CARE-X report issue "Invariant check incorrectly fixed".

```
function deployPool(PoolDeployment calldata deploymentParameters) external override returns (address) {
```
```
poolCommitter.initialize(..., deploymentParameters.invariantCheck, ... ); // version 1 of
,! invariantCheck
```
```
ILeveragedPool.Initialization memory initialization = ILeveragedPool.Initialization({
```
```
_invariantCheckContract: invariantCheck, // version 2 of invariantCheck
```
```
});
```
**Recommendation:** The code should be changed to:

```
function deployPool(PoolDeployment calldata deploymentParameters) external override returns (address) {
```
- poolCommitter.initialize(..., deploymentParameters.invariantCheck, ... );
+ poolCommitter.initialize(..., invariantCheck, ... );
}

In addition, theinvariantCheckmember of structPoolDeploymentinIPoolFactory.solshould be removed to
prevent mistakes.

**Tracer:** Valid. Fixed as part of CARE-X commit 98c76bf

**Spearbit:** Acknowledged.
