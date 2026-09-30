# [C] TradableStaking: shares accounting is corrupted

## Summary
Severity: Critical
Contest weight: 0.5990
Dataset id: 16119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current implementation of the TradableStaking contract, the staking function gives any user staking in the protocol the total amount of outstanding shares instead of the ones entitled by the user. This is due to a typo on line 174. Here, the user gets shares: uint64(shares) instead of shares: uint64(userShares), where shares is the global variable representing the total number of outstanding shares, which gets corrupted by the typo.
This allows any staking user to withdraw and receive rewards as if they owned all the shares of the vault.
For clarification, take a look at the following code (a simplification of the logic used in the TradableStaking contract).
```solidity
uint96 public balance;
uint64 public staked;
uint64 public shares; //total shares of staking pool at the moment
function _stake(address user, uint256 amount) internal{
    uint256 userShares = amount * shares / balance;
    balance += uint96(amount);
    staked += uint64(amount);
    shares += uint64(userShares);
    stakes[user] = Stake({
        owner: user,
        amount: uint64(amount),
        shares: uint64(shares),
        timestamp: uint32(block.timestamp)
    });
    emit StakeValidated(user, amount, shares);
}
```
The event StakeValidated() is also emitting the wrong variable, it should be userShares instead of shares.

## Recommendation
On line 174, replace shares: uint64(shares) with shares: uint64(userShares), same goes for the event on line 186. The logic for deposits, withdrawals and rewards should also be heavily tested.
