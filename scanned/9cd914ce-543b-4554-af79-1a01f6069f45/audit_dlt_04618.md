# [M] Loss ERC20 tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/16
Type: sherlock-finding

## Details
Atarpara

medium

# Loss ERC20 tokens

## Summary
Some user not get their stuck erc20 token.

## Vulnerability Detail
assume 2 users deposits 1000 token on staking module by mistake. Now RECOVERY_ROLE can transfer all erc20 into only one users and other user loss their token. Some issue with TEL token. 

## Impact
Loss ERC20 token.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L443-L450

```solidity
    /// @notice rescues any stuck erc20
    /// @dev if the token is TEL, then it only allows maximum of balanceOf(this) - _totalStaked to be rescued
    function rescueTokens(IERC20Upgradeable token, address to) external onlyRole(RECOVERY_ROLE) {
        if (address(token) == tel) {
            // if the token is TEL, only remove the extra amount that isn't staked
            token.safeTransfer(to, token.balanceOf(address(this)) - _totalStaked);
        }
        else {
            // if the token isn't TEL, remove all of it
            token.safeTransfer(to, token.balanceOf(address(this)));
        }
    }
```
## Tool used

Manual Review

## Recommendation
add amount parameter into recuseToken function. 

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/16_
