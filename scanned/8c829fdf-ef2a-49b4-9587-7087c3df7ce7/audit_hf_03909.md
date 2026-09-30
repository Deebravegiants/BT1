# [M] PoolRegistry#upgradePoolshould call SimpleRamp#refres

## Summary
Severity: Medium
Contest weight: 0.5900
Dataset id: 20208
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After a pool is upgraded, ramp#refreshExtern should be called in order to connect it to the new version of the pool. Although it is an external function which anyone can call, an unlucky user might attempt to use the ramp after a pool has been upgraded, but the ramp hasn't yet been refreshed and end up losing their funds. Problem 1 After a pool is successfully upgraded, all liquid assets are transferred to its new version. This is important as the ramp calculates the share price based of the assets in the pool + totalBorrowed. If the pool is upgraded, but the ramp isn't updated a user withdrawing will receive their assets based only on totalBorrowed
```solidity
function redeem(
    uint256 shares,
    address receiver,
    address owner,
    uint256
) public ownerIsCaller(owner) returns (uint256 assets) {
    assets = pool.convertToAssets(shares);
    _processExit(owner, receiver, shares, assets);
}
```
```solidity
function convertToAssets(uint256 shares) public view returns (uint256) {
    uint256 supply = liquidStakingToken.totalSupply(); // Saves an extra SLOAD if totalSupply is non-zero.
    return supply == 0 ? shares : shares.mulDivDown(totalAssets(), supply);
}
```
```solidity
function totalAssets() public view override returns (uint256) {
    return asset.balanceOf(address(this)) + totalBorrowed +
    preStake.totalValueLocked() - feesCollected;
    totalBorrwed
}
```
In the case where the old pool has a low amount of totalBorrowed the innocent user will burn their iFIL and receive very little wFIL Problem 2 Another issue which arises from not calling refreshExtern is that if there is FIL/wFIL in the ramp contract and a user calls recoverFIL after the pool has been upgraded, but before refreshExtern has been called, the FIL from the ramp will be sent to the old pool. from where the funds cannot be later retrieved. Loss of funds for an innocent user. Forever stuck funds.

## Recommendation
Add the following line of code to PoolRegistry#upgradePool oldPool.ramp.refreshExtern();
