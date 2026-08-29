# [M] [ADRIRO-NEW-H-02] Users loses their share of rewards while waiting for withdrawal

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/47
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/AfEth.sol#L206


# Vulnerability details

## Summary

Withdrawals in AfEth undergo a delay until the underlying CVX tokens can be withdrawn. Depositors need to request a withdrawal and wait until the required withdrawal epoch before making their withdrawal effective. During this period of time, they will lose their share of any compounded reward into SafEth.

## Impact

Withdrawals in AfEth are first requested using the `requestWithdraw()`. As we can see in the implementation, the function will calculate the number of SafEth tokens corresponding to the user's share (`safEthWithdrawAmount`) and store that information to be used when the withdrawal can be finally executed.

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/AfEth.sol#L222-L236

```solidity
222:         uint256 safEthBalance = safEthBalanceMinusPending();
223: 
224:         uint256 safEthWithdrawAmount = (withdrawRatio * safEthBalance) / 1e18;
225: 
226:         pendingSafEthWithdraws += safEthWithdrawAmount;
227: 
228:         withdrawIdInfo[latestWithdrawId]
229:             .safEthWithdrawAmount = safEthWithdrawAmount;
230:         withdrawIdInfo[latestWithdrawId]
231:             .votiumWithdrawAmount = votiumWithdrawAmount;
232:         withdrawIdInfo[latestWithdrawId].vEthWithdrawId = vEthWithdrawId;
233: 
234:         withdrawIdInfo[latestWithdrawId].owner = msg.sender;
235:         withdrawIdInfo[latestWithdrawId].amount = _amount;
236:         withdrawIdInfo[latestWithdrawId].withdrawTime = withdrawTimeBefore;
```

Line 224 calculates the amount based on the user's share and the total number of SafEth tokens held by the AfEth contract. This amount **gets fixed at this moment** and is stored in the `withdrawIdInfo` mapping, which is later used by `withdraw()` to send the funds to the user:

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/AfEth.sol#L284-L290

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/47_
