# [C] The fee mechanism is not enforced

## Summary
Severity: Critical
Contest weight: 0.2421
Dataset id: 13556
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The codebase is using a fee mechanism where the users pay a fee for using some functionality. An example where this is done is the Compound::depositETHV2 method, as we can see here:
```solidity
function depositETHV2(
    address _recipient,
    uint256 _proxyFeeInWei
) external payable nonETHReuse {
    address _cEther = address(cEther);
    ICEther(_cEther).mint{value: msg.value - _proxyFeeInWei}();
```
The problem with this approach is that the value of the fee is controlled by the user through the _proxyFeeInWei argument, meaning he can always send 0 value to it so he doesn't pay any fees.

## Recommendation
Rearchitecture the fees approach so that a fee can be enforced on users, for example by using a sensible admin set value for it.
