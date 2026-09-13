# [M] Queue checks address balance instead of deposited amount

## Summary
Severity: Medium
Reporter: carrot
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Queue checks address balance instead of deposited amount

## Summary

Queue check address balance instead of deposited amount for checking against a Max TVL. This can cause the protocol to stop accepting deposits while having no returns if an attacker sends the contract WETH directly. 

## Vulnerability Detail

Queue contract can be stopped from working by sending WETH directly. This will ensure no vault share or claim token is minted but the protocol will think it has reached the limit. This can also throw off internal calculations as pricepershare will be set to 1e18 without any claim tokens minted.

## Impact
Sent WETH will be stuck inside vault. Anyone adding in even 1 wei will have access to all WETH sent directly to the queue account.
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

        QueueStorage.Layout storage l = QueueStorage.layout();

        // the price-per-share can be queried if the claim token id is provided
        l.pricePerShare[currentTokenId] = pricePerShare;

        // increment the epoch id
        l.epoch = l.epoch + 1;

        emit ProcessQueuedDeposits(
            l.epoch,
            deposits,
            pricePerShare,
            shares,
            claimTokenSupply
        );
    }
```
## Tool used

Manual Review

## Recommendation
Keep track of total user deposits, and send that amount forward to the vault. Allow retrieval of any WETH sent directly to the contract.
