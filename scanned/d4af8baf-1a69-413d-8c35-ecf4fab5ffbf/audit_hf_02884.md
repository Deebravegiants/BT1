# [H] An off-by-one error can DoS the bribe method

## Summary
Severity: High
Contest weight: 0.7511
Dataset id: 16164
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The purpose of the bribe function is to allow the TradFiLines NFT holders to trade them for one extra hour outside of the NYSE/NASDAQ trading hours. This can be done by paying the bribeAmount which is set to 0.01 ether initially. However, a wrong comparison operator in the require statement will revert if the bribeAmount is equal to 0.01 ether.
```solidity
function bribe(uint year, uint month, uint day, uint hour) payable external {
    require(!bribedHour[year][month * 10000 + day * 100 + hour], "This hour is already bribed for and open");
    require(msg.value > bribeAmount, string(abi.encodePacked("The required bribe amount is ", Strings.toString(bribeAmount)))); //@audit - off by one error
}
```
The problem is that when the function reverts, the thrown error will say that exactly the bribeAmount is required making it confusing for the user. A user will potentially try again with the same amount of ether but the function will revert again because msg.value should be more than 0.01 ether. This will discourage users to use the bribe function putting it in a state of DoS.

## Recommendation
Change the require statement as below:
```solidity
-require(msg.value > bribeAmount)
+require(msg.value >= bribeAmount)
```
