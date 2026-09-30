# [M] AdjustmentFlow for feeDistributionPool is streamed

## Summary
Severity: Medium
Contest weight: 0.4477
Dataset id: 23041
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
AdjustmentFlow for feeDistributionPool is streamed to SuperBoring contract, but there is no way to rescue it.
From this doc https://github.com/superfluid-finance/protocol-monorepo/wiki/General-Distribution-Agreement#adjustment-flow, we know that if a pool's flowRate cannot be fully divided by the total amount of units, the remainder in the flowRate is streamed to the pool admin.
In the case of the feeDistributionPool, the admin is the controller, which is the SuperBoring protocol. However, once the inToken is streamed to the SuperBoring protocol, there is no method to rescue it, so it remains locked inside forever.
This is not a trivial amount. Consider 1e5 users staking for a Torex, each with 1e5 units, making the total unit amount 1e10, which is the upper limit for the flowRate streamed to the SuperBoring protocol. This means 1e10 tokens are streamed to the SuperBoring protocol per second. If the stream continues for one day, it would decimals). This is a non-trivial for some expensive tokens.
```solidity
feeDistributionPool = _inToken.createPool(address(controller), PoolConfig({
    transferabilityForUnitsOwner: false,
    distributionFromAnyAddress: true
}));
function _onInFlowChanged(ISuperToken superToken, address sender, int96 prevFlowRate, uint256 lastUpdated,
bytes memory ctx) internal returns (bytes memory newCtx)
{
    ...
    // update fee distribution flow rate, this requires the buffer cost taken as part of back adjustment.
    newCtx = _inToken.distributeFlowWithCtx(address(this), feeDistributionPool, _requestedFeeDistFlowRate, newCtx);
    (, _actualFeeDistFlowRate, _feeDistBuffer) = _inToken.getGDAFlowInfo(address(this), feeDistributionPool);
}
```
An non-trivial amount of token may be locked up in SuperBoring contract.

## Recommendation
Add a token rescue function for admins in SuperBoring contract.
