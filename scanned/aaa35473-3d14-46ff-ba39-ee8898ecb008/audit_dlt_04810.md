# [H] User can remove the adapter's stake token balance from the AutoRoller.sol by calling claimRewards

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-sense
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-sense-judging/issues/37
Type: sherlock-finding

## Details
ctf_sec

high

# User can remove the adapter's stake token balance from the AutoRoller.sol by calling claimRewards

## Summary

User can remove the adapter's stake token address from the AutoRoller.sol by calling claimRewards

## Vulnerability Detail

Let us look into this piece of code:

```solidity
    /// @notice Transfer any token not included in the set {asset,yt,pt,space} to the rewards recipient.
    /// @param coin address of the coin to transfer out.
    function claimRewards(ERC20 coin) external {
        require(coin != asset);
        if (maturity != MATURITY_NOT_SET) {
            require(coin != ERC20(address(yt)) && coin != pt && coin != ERC20(address(space)));
        }
        coin.transfer(rewardRecipient, coin.balanceOf(address(this)));
    }
```

This function can be by anyone to help the rewardRecipient collect fee or it can be used to rescue the token that sent to the AutoRoller.sol contract.

However, the function  failed to check if the passed in coin is equal to the adapter's stake token.

```solidity
/// @param stakeSize the adapter's stake size.
function onSponsorWindowOpened(ERC20 stake, uint256 stakeSize) external {
  if (msg.sender != address(adapter)) revert OnlyAdapter();

  stake.safeTransferFrom(lastRoller, address(this), stakeSize);

  // Allow the Periphery to move stake for sponsoring the Series.
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sense-judging/issues/37_
