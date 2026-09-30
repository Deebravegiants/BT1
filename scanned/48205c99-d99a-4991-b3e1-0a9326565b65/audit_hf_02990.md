# [M] Use call with value instead of transfer

## Summary
Severity: Medium
Contest weight: 0.6554
Dataset id: 16662
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The problem in the below snippet of code in burn():
```solidity
payable(tx.origin).transfer(nativeAmount - fee);
```
is that tx.origin won't work if the receiver of the rest of the native tokens is a multi-sig wallet, because tx.origin works only with externally owned accounts (EOAs) and multi-sig wallets are smart contracts.

## Recommendation
Instead, if transferring native assets to multi-sig wallet is likely to be expected, msg.sender should be used instead of tx.origin because msg.sender will return the caller of the function whether it is a smart contract or a EOA. Also if you decide to use msg.sender here, you should also change the ether transferring method from .transfer to .call with value and check if the result is a success like this:
```solidity
(bool success, bytes memory data) = payable(msg.sender).call{value: msg.value}("");
require(success, "Transfer failed.");
```
fallback function that takes up more than the 2300 gas which is the limit of transfer. Also the .call method should be used instead of transfer in burnTo() for the same reasons:
```solidity
if (fee > 0) {
    bank.agency.transfer(fee);
    bank.totalBurnFee += fee;
    payable(sink).transfer(nativeAmount - fee);
}
```
The bank.agency and sink can be smart contracts or multi-sig wallets that requires more than 2300 gas. ZKT_Tsunami.md
