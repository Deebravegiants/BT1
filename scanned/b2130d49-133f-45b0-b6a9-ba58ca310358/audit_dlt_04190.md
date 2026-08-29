# [M] Check return value of sellQuote and sellBase

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/86
Type: sherlock-finding

## Details
defsec

medium

# Check return value of sellQuote and sellBase

## Summary

In the _multiSwap function, the return value of sellQuote and sellBase is not checked to be ensure that transaction execution is successfully completed.

## Vulnerability Detail

In the DODO [documentation](https://dodoex.github.io/docs/docs/contractUseGuide/), It is mentioned that `Before the end, traders are advised to check the value of receiveBaseAmount to ensure the safe execution of the transaction.` However this is not checked in the multiSwap function.

## Impact

The received amount can be lost due to slippage.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L428

```solidity
                if (curPoolInfo.direction == 0) {
                    IDODOAdapter(curPoolInfo.adapter).sellBase(
                        assetFrom[i],
                        curPoolInfo.pool,
                        curPoolInfo.moreInfo
                    );
                } else {
                    IDODOAdapter(curPoolInfo.adapter).sellQuote(
                        assetFrom[i],
                        curPoolInfo.pool,
                        curPoolInfo.moreInfo
                    );
                }
            }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/86_
