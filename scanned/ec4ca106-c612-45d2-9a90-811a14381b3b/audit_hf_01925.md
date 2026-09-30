# [H] Wrong implementation of `withdrawAdminFees`

## Summary
Severity: High
Contest weight: 0.7498
Dataset id: 10550
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[SwapUtils.sol#L1053-L1062](https://github.com/code-423n4/2022-06-connext/blob/b4532655071566b33c41eac46e75be29b4a381ed/contracts/contracts/core/connext/libraries/SwapUtils.sol#L1053-L1062)  

```solidity
function withdrawAdminFees(Swap storage self, address to) internal {
  IERC20[] memory pooledTokens = self.pooledTokens;
  for (uint256 i = 0; i < pooledTokens.length; i++) {
    IERC20 token = pooledTokens[i];
    uint256 balance = self.adminFees[i];
    if (balance != 0) {
      token.safeTransfer(to, balance);
    }
  }
}
```

`self.adminFees[i]` should be reset to 0 every time it’s withdrawn. Otherwise, the `adminFees` can be withdrawn multiple times.

The admin may just be unaware of this issue and casually `withdrawAdminFees()` from time to time, and rug all the users slowly.

## Recommendation
Change to:

```solidity
function withdrawAdminFees(Swap storage self, address to) internal {
  IERC20[] memory pooledTokens = self.pooledTokens;
  for (uint256 i = 0; i < pooledTokens.length; i++) {
    IERC20 token = pooledTokens[i];
    uint256 balance = self.adminFees[i];
    if (balance != 0) {
      self.adminFees[i] = 0;
      token.safeTransfer(to, balance);
    }
  }
}
```

[connext/nxtp@8eef974](https://github.com/connext/nxtp/pull/1450/commits/8eef974724bf2b9cdd506a1a63d8cc869303c3e5)

Completely agree with the validity of this finding. Even if the admin was _not_ malicious, the bug will still continue to withdraw additional fees which were not included as part of the swap calculations. LPs would lose considerable value as a result.
