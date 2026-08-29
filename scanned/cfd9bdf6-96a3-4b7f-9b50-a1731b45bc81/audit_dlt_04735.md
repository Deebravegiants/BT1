# [M] H-01 First Call per `_getCurrentTokenId` to Process Deposits can get rekt via front-run

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/131
Type: sherlock-finding

## Details
GalloDaSballo

medium

# H-01 First Call per `_getCurrentTokenId` to Process Deposits can get rekt via front-run

## Summary

If `_totalSupply` for the `currentTokenId` is zero, the Queue will assume that it will mint with a ppfs of ONE_SHARE.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L202-L203

```solidity
    function processDeposits() external onlyVault {
        ...
        uint256 currentTokenId = QueueStorage._getCurrentTokenId();
        uint256 claimTokenSupply = _totalSupply(currentTokenId);
        uint256 pricePerShare = ONE_SHARE;

        if (shares <= 0) {
            pricePerShare = 0;
        } else if (claimTokenSupply > 0) {
            pricePerShare = (pricePerShare * shares) / claimTokenSupply;
        }

```

This may not be the case, as a front-runner could deposit directly into the vault, causing a rebase of the Vault.

Additionally, since the `currentTokenId` is used, there may be some totalSupply from previous tokenIds, this again would allow to have a rebase of the Vault that would cause the break the assumption that shares are worth `ONE_SHARE`.

## Vulnerability Detail

## Impact

Loss of shares if price per share is different from `ONE_SHARE`

## Code Snippet

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/131_
