# [M] Reenterancy in `_sendSherRewardsToOwner()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-sherlock
Published: 2022-01-23
Source: https://github.com/code-423n4/2022-01-sherlock-findings/issues/60
Type: code-finding

## Details
# Handle

kirk-baird


# Vulnerability details

## Impact

This is a reentrancy vulnerability that would allow the attacker to drain the entire SHER balance of the contract.

Note: this attack requires gaining control of execution `sher.transfer()` which will depend on the implementation of the SHER token. Control may be gained by the attacker if the contract implements ERC777 or otherwise makes external calls during `transfer()`.

## Proof of Concept

See [_sendSherRewards](https://github.com/code-423n4/2022-01-sherlock/blob/main/contracts/Sherlock.sol#L442)

```solidity
  function _sendSherRewardsToOwner(uint256 _id, address _nftOwner) internal {
    uint256 sherReward = sherRewards_[_id];
    if (sherReward == 0) return;

    // Transfers the SHER tokens associated with this NFT ID to the address of the NFT owner
    sher.safeTransfer(_nftOwner, sherReward);
    // Deletes the SHER reward mapping for this NFT ID
    delete sherRewards_[_id];
  }
```

Here `sherRewards` are deleted after the potential external call is made in `sher.safeTransfer()`. As a result if an attacker reenters this function `sherRewards_` they will still maintain the original balance of rewards and again transfer the SHER tokens.

As `_sendSherRewardsToOwner()` is `internal` the attack can be initiated through the `external` function `ownerRestake()` [see here.](https://github.com/code-423n4/2022-01-sherlock/blob/main/contracts/Sherlock.sol#L595)

Steps to produce the attack:

1) Deploy attack contract to handle reenterancy
2) Call `initialStake()` from the attack contract with the smallest `period`
3) Wait for `period` amount of time to pass

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-sherlock-findings/issues/60_
