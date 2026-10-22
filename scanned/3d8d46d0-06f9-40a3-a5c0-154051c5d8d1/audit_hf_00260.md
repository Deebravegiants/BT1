# [M] Bypass zap timelock

## Summary
Severity: Medium
Contest weight: 0.5563
Dataset id: 1319
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The default value of `inventoryLockTime` in `NFTXStakingZap` is `7 days` while `DEFAULT_LOCKTIME` in `NFTXInventoryStaking` is 2 ms. These timelock value are used in `NFTXInventoryStaking` to eventually call `_timelockMint` in `XTokenUpgradeable`.

```solidity
function _timelockMint(address account, uint256 amount, uint256 timelockLength) internal virtual {
  uint256 timelockFinish = block.timestamp + timelockLength;
  timelock[account] = timelockFinish;
  emit Timelocked(account, timelockFinish);
  _mint(account, amount);
}
```

The applicable timelock is calculated by `block.timestamp + timelockLength`, even when the existing timelock is further in the future. Therefore, one can reduce their long (e.g. 7 days) timelock to 2 ms calling `deposit` in `NFTXInventoryStaking`.

## Recommendation
```solidity
function _timelockMint(address account, uint256 amount, uint256 timelockLength) internal virtual {
  uint256 timelockFinish = block.timestamp + timelockLength;
  if(timelockFinish > timelock[account]){
    timelock[account] = timelockFinish;
    emit Timelocked(account, timelockFinish);
  }
  _mint(account, amount);
}
```

After taking another look, this is definitely accurate. Thank you!

**[0xKiwi (NFTX) resolved](https://github.com/code-423n4/2021-12-nftx-findings/issues/178)**
