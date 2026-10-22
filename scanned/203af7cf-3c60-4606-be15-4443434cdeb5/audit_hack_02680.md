# [M] Use = 0 instead of <= 0

## Summary
Severity: Medium
Reporter: 8olidity
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L216
Type: audit-issue

## Details
# Use = 0 instead of <= 0

## Summary
Use = 0 instead of <= 0
## Vulnerability Detail
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L216
## Impact
Causing distress
## Code Snippet
```solidity
    function processDeposits() external onlyVault {
        uint256 deposits = ERC20.balanceOf(address(this));
        ERC20.approve(address(Vault), deposits);
        // the queue deposits their entire balance into the vault at the end of each epoch
        uint256 shares = Vault.deposit(deposits, address(this));

        // the shares returned by the vault represent a pro-rata share of the vault tokens. these
        // shares are used to calculate a price-per-share based on the supply of claim tokens for
        // that epoch. the price-per-share is used as an exchange rate of claim tokens to vault
        // shares when a user withdraws or redeems.
        uint256 currentTokenId = QueueStorage._getCurrentTokenId();
        uint256 claimTokenSupply = _totalSupply(currentTokenId);
        uint256 pricePerShare = ONE_SHARE;

        if (shares <= 0) {
            pricePerShare = 0;
        } else if (claimTokenSupply > 0) {
            pricePerShare = (pricePerShare * shares) / claimTokenSupply;
        }
```
Vault.deposit() returns a value of Uint256, and the shares type is also uint256.if (shares <= 0) {The judgement is meaningless. You can say shares = 0
## Tool used
vscode
Manual Review

## Recommendation
if (shares = 0)
