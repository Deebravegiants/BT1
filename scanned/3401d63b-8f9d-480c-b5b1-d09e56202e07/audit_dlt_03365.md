# [M] Fee on transfer token not supported

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-01-popcorn
Published: 2023-02-07
Source: https://github.com/code-423n4/2023-01-popcorn-findings/issues/503
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-popcorn//blob/main/src/utils/MultiRewardEscrow.sol#L100


# Vulnerability details

## Impact
If you are making a Lock fund for escrow using a fee on transfer token then contract will receive less amount (X-fees) but will record full amount (X). This becomes a problem as when claim is made then call will fail due to lack of funds. Worse, one user will unknowingly take the missing fees part from another user deposited escrow fund

## Proof of Concept
1. User locks token X as escrow which take fee on transfer
2. For same, he uses `lock` function which transfer funds from user to contract

```
 function lock(
    IERC20 token,
    address account,
    uint256 amount,
    uint32 duration,
    uint32 offset
  ) external {
...
 token.safeTransferFrom(msg.sender, address(this), amount);
...
escrows[id] = Escrow({
      token: token,
      start: start,
      end: start + duration,
      lastUpdateTime: start,
      initialBalance: amount,
      balance: amount,
      account: account
    });
...
}
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-popcorn-findings/issues/503_
