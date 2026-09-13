# [M] 7.15 Incorrect Cash Out Amount

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

Existing perpetual positions can be updated. Any perpetual position that is modified through
addToPerpetual or removeFromPerpetual results in the wrong cashOutAmount. Please consider
the following example in which all transactions happen shortly after each other. Hence, we assume that
the oracle prices do not change and are 1000 and 1125 respectively. Please note that changing oracle
prices can make the problem worse. We will also ignore fees in this example.

```
1.A new position is created and its cashOutAmount = 10 ETH, while committedAmount = 20 ETH.
The initialRate = 1125.
2.The position is updated through addToPerpetual and 1 ETH is added. The new committed
amount is calculated as 20 ETH * 1125 / 1000 = 22.5 ETH. Hence the new cashOutAmount is
calculated as 20 ETH + 10 ETH - 22.5 ETH + 1 ETH = 8.5 ETH. The initialRate remains 1125.
3.The user performs a cash out using cashOutPerpetual. The newly committed amount is
calculated as 20 ETH * 1125 / 1000 = 22.5 ETH. Hence the new cashOutAmount is calculated as
20 ETH + 8.5 ETH - 22.5 ETH = 6 ETH. Therefore, the user receives 6 ETH, despite depositing 11
ETH.
```
In short, whenever the oracle rates significantly deviate from each other, users can lose significant value.
This issue can grow in severity with fees, repetitive operations and price fluctuations.

Code corrected:

This issue has been addressed by only storing the initial rate. Hence, errors can no longer accumulate
with the number of actions.
