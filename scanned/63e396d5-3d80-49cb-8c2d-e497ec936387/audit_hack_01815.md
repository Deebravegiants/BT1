# [M] Use of external calls with a fixed amount of gas

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The converter smart contract uses the Solidity transfer() function to transfer Ether.

.transfer() and .send() forward exactly 2,300 gas to the recipient. The goal of this hardcoded gas stipend was to prevent reentrancy vulnerabilities, but this only makes sense under the assumption that gas costs are constant. Recently EIP 1884 was included in the Istanbul hard fork. One of the changes included in EIP 1884 is an increase to the gas cost of the SLOAD operation, causing a contract's fallback function to cost more than 2300 gas.

#### Examples


**code/contracts/converter/ConverterBase.sol:L228**
```solidity
_to.transfer(address(this).balance);
```


**code/contracts/converter/LiquidityPoolV2Converter.sol:L370**
```solidity
if (_targetToken == ETH_RESERVE_ADDRESS)
```


**code/contracts/converter/LiquidityPoolV2Converter.sol:L509**
```solidity
msg.sender.transfer(reserveAmount);
```

#### Recommendation

It's recommended to stop using .transfer() and .send() and instead use .call(). Note that .call() does nothing to mitigate reentrancy attacks, so other precautions must be taken. To prevent reentrancy attacks, it is recommended that you use the checks-effects-interactions pattern.
