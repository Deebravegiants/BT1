# [H] Bogus Collateralization With Evil Pools

## Summary
Severity: High
Contest weight: 0.5750
Dataset id: 12304
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The INIT Capital protocol has the built-in lending functionality and allows users to add additional collateral into existing positions. While examining the collateral-adding logic, we notice an issue that requires stricter validation on the given user input.
In the following, we show the implementation of the related collateralize() routine. As the name indicates, this routine is designed to add more collateral into a given position. While it does validate the pool mode as well as the given collateral pool, we notice the collateral token validation needs to be performed on the given _pool argument, not the query result from ILendingPool(_pool).underlyingToken() (line 193). As a result, a malicious actor may create an evil pool to bypass the validity check and create a fake top-up issue.
```solidity
function collateralize(uint _posId, address _pool) public virtual onlyPosOwner(_posId) nonReentrant {
    IConfig _config = IConfig(config);
    // check mode
```

## Recommendation
Revisit the above routine to properly validate the user input. Note this issue also affects another routine, i.e., setPositionMode().
