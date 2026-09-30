# [M] Beware Of Malicious Adapters

## Summary
Severity: Medium
Contest weight: 0.4619
Dataset id: 15001
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Situation:
The following functions allow for interaction with any adapter. These adapters could be malicious. No additional checks are made on the validity of the adapter.
Through the adapter, a re-entrant call could be made and no nonReentrant modifier is used in the Periphery contract.
function sponsorSeries(address adapter, ... )
function swapTargetForZeros(address adapter, ... )
function swapUnderlyingForZeros(address adapter, ... )
function swapTargetForClaims(address adapter, ... )
function swapUnderlyingForClaims(address adapter, ... )
function swapZerosForTarget(address adapter, ... )
function swapZerosForUnderlying(address adapter, ... )
function swapClaimsForTarget(address adapter, ... )
function swapClaimsForUnderlying(address adapter, ... )
function addLiquidityFromTarget(address adapter, ... )
function addLiquidityFromUnderlying(address adapter, ... )
function removeLiquidityToTarget(address adapter, ... )
function removeLiquidityToUnderlying(address adapter, ... )
function migrateLiquidity(address srcAdapter, address dstAdapter,...)
Within Periphery.sol, there are several locations where a safeApprove() is given to an adapter. Frequently, the token for which the safeApprove() is given is also derived from the adapter that can also be manipulated. These are the relevant lines:
```solidity
ERC20(target).safeApprove(address(adapterClone), type(uint256).max);
ERC20(Adapter(adapter).underlying()).safeApprove(adapter, uBal); // approve adapter to pull uBal
ERC20(Adapter(adapter).underlying()).safeApprove(adapter, uBal); // approve adapter to pull underlying
ERC20(Adapter(adapter).target()).safeApprove(adapter, tBal); // approve adapter to pull target
underlying.safeApprove(adapter, uBal);
ERC20(Adapter(adapter).target()).safeApprove(adapter, tBal);
if (_allowance < amount) target.safeApprove(address(adapter), type(uint256).max);
```
A malicious adapter could therefore steal any tokens present in Periphery contract. This is true for both now and in the future, as the approval will persist.

## Recommendation
Consider using a whitelist for the adapters. Add a nonReentrant modifier to the function that use the adapter. Make sure no tokens will be stored in the Periphery contract (now and in the future).
