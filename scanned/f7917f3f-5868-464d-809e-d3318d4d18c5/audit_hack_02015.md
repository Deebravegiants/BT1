# [H] 6.1 Gas Griefing

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

ERC20Farmable calls farm contracts in every call to farmedPerToken() to query information with
IFarm.farmedSinceCheckpointScaled() on how many rewards have been released so far. Even
though that call is handled with a try/catch block to prevent the target contract from reverting
maliciously, it is still possible that the farm consumes all gas.

```
1.A malicious farm honeypots users into joining.
2.The malicious farm contract is upgraded through an upgradeability pattern.
```
```
3.Every call to farmedSinceCheckpointScaled() consumes all gas.
```
Now, following is not possible:

- any ERC20Farmable transfer from an affected user
- any ERC20Farmable transfer to an affected user
- exiting the malicious farm
- Claiming from the malicious farm

Ultimately, tokens will be locked for affected users.

Code corrected:


The call to IFarm.famedSinceCheckpointScaled() now has a gas limit. If the gas limit of 200000 is
exceeded, the failure is handled by behaving equivalently to a revert in the farm contract.

Additionally, the static-call was wrapped inside an assembly block to prevent the return data bomb issue
in the Solidity compiler (documented here: https://github.com/ethereum/solidity/issues/12306).
