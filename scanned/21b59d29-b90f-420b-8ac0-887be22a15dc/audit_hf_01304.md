# [M] Beneficiaries can grief senders on ETH transfers

## Summary
Severity: Medium
Contest weight: 0.6523
Dataset id: 6225
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Functions such as confirmOrderV3 allow a sender to the send funds to a beneficiary via an external call in case of the asset being ETH.
```solidity
require(settleNativeOrToken(amount, asset, target, msg.sender), "RO#2");
```
The function makes an external call to the beneficiary where they can basically spend the remaining gas of the transaction and make the sender pay for a huge increase on gas fees:
```solidity
if (asset == address(0)) {
    (bool sent, ) = beneficiary.call{value: amount}("");
    return sent;
}
```

## Recommendation
As limiting the gas being forwarded does not prevent a return bomb attack, the only choice is to use a low level call to avoid loading the returned data into memory:
```solidity
assembly {
    success := call(gasLimit, receiver, amount, 0, 0, 0, 0)
}
```
