# [M] The final order that sells out the vault can oversell the vault

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/72
Type: sherlock-finding

## Details
0x52

high

# The final order that sells out the vault can oversell the vault

## Summary

The final order that pushes the total number of contract sold over the threshold isn't adjusted which can cause the vault to become oversold.

## Vulnerability Detail

[AuctionInternal.sol#L391-L395](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L391-L395)

    if (totalContractsSold + data.size >= totalContracts) {
        auction.lastPrice64x64 = data.price64x64;
        auction.totalContractsSold = totalContracts;
        return true;
    }

In AuctionInternal#_processOrders the following lines are executed when the totalContractsSold exceeds totalContracts, which means that the options are now fully sold out. auction.totalContractsSold is capped to the max number of sellable contracts but the sum of contracts sold to those order can be greater than that.

Example:
100 contracts are available for sale. First user A buys 50 contract @ 0.5 each. Next user B buys 80 contracts @ 0.3 each. auction.totalContractsSold would be set to 100 but a total of 130 contracts have actually been sold. If they turn out to be ITM it could cause insolvency for the vault.

## Impact

Oversized losses or vault insolvency

## Code Snippet

[AuctionInternal.sol#L359-L416](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L359-L416)

## Tool used

Manual Review

## Recommendation

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/72_
