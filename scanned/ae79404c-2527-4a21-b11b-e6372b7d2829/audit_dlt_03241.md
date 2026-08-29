# [M] Unsafe usage of `msg.value` in a loop

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-19
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/367
Type: code-finding

## Details
### Lines of code

--------------

[140](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/TapiocaWrapper.sol#L140-L147)

### Vulnerability details

-------------

The value of `msg.value` in a transaction's call never gets updated, even if the called contract ends up sending some or all of the Eth to another contract. This means that using `msg.value` in a `for`- or `while`-loop, without extra accounting logic, will either lead to the transaction reverting (when there are no longer sufficient funds for later iterations), or to the contract being drained (when the contract itself has an Eth balance)

```solidity
File: contracts/TapiocaWrapper.sol

140          for (uint256 i = 0; i < _call.length; i++) {
141              (success, results[i]) = payable(_call[i].toft).call{
142                  value: msg.value
143              }(_call[i].bytecode);
144              if (_call[i].revertOnFailure && !success) {
145                  revert TapiocaWrapper__TOFTExecutionFailed(results[i]);
146              }
147:         }

```


### Assessed type

------------

other
