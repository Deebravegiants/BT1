# [M] FeeBuyback's submit can lose funds if used with zero addresses, which is allowed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/97
Type: sherlock-finding

## Details
hyh

medium

# FeeBuyback's submit can lose funds if used with zero addresses, which is allowed

## Summary

It's now allowed to use FeeBuyback's submit() with zero `wallet` or zero `_aggregator`, while low level calls are performed with both addresses.

## Vulnerability Detail

Low-level calls submit() perform will return success if used with zero addresses as the failure need to come from the contract that is being called, while zero address will not do that. In both cases no operations will be performed.

## Impact

Not executing the primary swap, but paying the fee is the fund loss for an owner.

Executing the primary swap, but not paying the fee as there is no TEL on the balance is the fund loss for a recipient.

Also, when MATIC is used the native funds sent to zero address via `_aggregator.call{value: msg.value}(swapData)` end up being lost.

## Code Snippet

Both `_aggregator` (in constructor) and `wallet` (in submit() below) aren't checked to be non-zero:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L28-L33

```solidity
  constructor(address aggregator_, address safe_, IERC20 telcoin_, ISimplePlugin referral_) TieredOwnership() {
    _aggregator = aggregator_;
    _safe = safe_;
    _telcoin = telcoin_;
    _referral = referral_;
  }
```

Low-level calls submit() perform will be successful if the address called (`wallet`, or `_aggregator` later) is zero:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L35-L82

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
    //Perform user swap first
    //Verify success
    (bool walletResult,) = wallet.call{value: 0}(walletData);
    require(walletResult, "FeeBuyback: wallet transaction failed");

    ...

    //Perform secondary swap from fee token to TEL
    //do simple transfer from and submit
    (bool swapResult,) = _aggregator.call{value: msg.value}(swapData);
    require(swapResult, "FeeBuyback: swap transaction failed");
    _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
    require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
    return true;
  }
```

Notice, that `_telcoin.balanceOf(address(this))` is allowed to be zero, which can happen as the secondary swap become a noop when `_aggregator` is zero.

In this case the funds will be lost as the native funds transfer executes even if the address is zero, while for the reverting to happen the contract have to indicate this, which will not be happening.

## Tool used

Manual Review

## Recommendation

Control for both `_aggregator` and `wallet` to be non-zero:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L28-L33

```solidity
  constructor(address aggregator_, address safe_, IERC20 telcoin_, ISimplePlugin referral_) TieredOwnership() {
+   require(_aggregator != address(0), "FeeBuyback: zero aggregator");
    _aggregator = aggregator_;
    _safe = safe_;
    _telcoin = telcoin_;
    _referral = referral_;
  }
```

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L35-L82

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
+   require(wallet != address(0), "FeeBuyback: zero wallet");
    //Perform user swap first
    //Verify success
    (bool walletResult,) = wallet.call{value: 0}(walletData);
    ...
```
