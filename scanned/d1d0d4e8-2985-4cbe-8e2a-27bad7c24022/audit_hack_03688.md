# [M] FeeBuyback.sol#submit is not pausable

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L34-L47
Type: audit-issue

## Details
# FeeBuyback.sol#submit is not pausable

## Summary

FeeBuyback.sol#submit is not pausable

## Vulnerability Detail

In FeeBuyBack, the comment states that the function submit can be paused.

```solidity
  /**
   * @notice submits wallet transactions
   * @dev a secondary swap may occur
   * @dev staking contract updates may be made
   * @dev function can be paused
   * @param wallet address of the primary transaction
   * @param walletData bytes wallet data for primary transaction
   * @param token address the token that is being swapped from in a secondary transaction
   * @param amount uint256 the quantity of the token being swapped
   * @param swapData bytes swap data from primary transaction
   * @return boolean representing if a referral transaction was made
   */
  function submit(address wallet, bytes memory walletData, address token, address recipient, uint256 amount, bytes memory swapData) external override payable onlyOwner() returns (bool) {
```

note the line:

```solidity
@dev function can be paused
```

However, the function submit is missing WhenNotPaused modifier, unlike the stake function in StakingModule.sol

```solidity
function stake(uint256 amount) external whenNotPaused nonReentrant
```

## Impact

FeeBuyback.sol#submit is not pausable

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L34-L47

## Tool used

Manual Review

## Recommendation

We recommend the project add the pause feature and use WhenNotPaused modifier in FeeBuyBack.sol contract.
