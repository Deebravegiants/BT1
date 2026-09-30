# [H] The setValue() will revert because of a wrong time unit

## Summary
Severity: High
Contest weight: 0.7427
Dataset id: 16163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function setValue in CircuitBreaker.sol allows you to update the oracle floor value by reading the Chainlink oracle.
Now lets take a look at the second require statement in it:
```solidity
require(updatedAt - lastTimestamp > 1000*60*60*12, "The value can only be updated after 12 hours. If the price moves a lot before 12 hours have passed, the breaker should be called");
```
The math 1000*60*60*12 is equal to 43,200,000 which is expected to be 12 hours like the revert string says. And yes it is 12 hours but in milliseconds and we are comparing it to a unix timestamp values taken from the oracle updateAt and lastTimestamp which are in seconds. So 43,200,000 seconds will be equal to 500 days and not 12 hours. Which will DOS the function because it will revert every time if the oracle is fetching the right data.

## Recommendation
Create a storage variable for example uint256 public updateTime = 12 hours; which is 43,200 seconds. And now you can re-write the require statement as:
```solidity
require(updatedAt - lastTimestamp > updateTime, "The value can only be updated after 12 hours");
```
