# [M] Queue deposit doesnt take account of fee-on-transfer tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/96
Type: sherlock-finding

## Details
carrot

medium

# Queue deposit doesnt take account of fee-on-transfer tokens

## Summary
Queue deposit function does not take account of fee-on-transfer tokens.
## Vulnerability Detail
Queue deposit takes an amount as input and mints claims equal to that amount without checking how many tokens are actually received. For fee-on-transfer tokens, this can lead to more claims than actual tokens present.
## Impact
Late redeemers can be left without tokens as early redeemers claim more tokens than they deserve since foo-on-transfer tokens are not accounted for.
## Code Snippet
```solidity
function _deposit(QueueStorage.Layout storage l, uint256 amount) internal {
        require(amount > 0, "value exceeds minimum");

        // the maximum total value locked is the sum of collateral assets held in
        // the queue and the vault. if a deposit exceeds the max TVL, the transaction
        // should revert.
        uint256 totalWithDepositedAmount =
            Vault.totalAssets() + ERC20.balanceOf(address(this));
        require(totalWithDepositedAmount <= l.maxTVL, "maxTVL exceeded");

        // prior to making a new deposit, the vault will redeem all available claim tokens
        // in exchange for the pro-rata vault shares
        _redeemMax(msg.sender, msg.sender);

        uint256 currentTokenId = QueueStorage._getCurrentTokenId();

        // the queue mints claim tokens 1:1 with collateral deposited
        _mint(msg.sender, currentTokenId, amount, "");

        emit Deposit(l.epoch, msg.sender, amount);
    }
```
## Tool used


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/96_
