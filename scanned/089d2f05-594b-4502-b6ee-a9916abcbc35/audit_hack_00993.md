# [M] LDO incident: On September 10, according to on-chain intelligence from the SlowMist security team, when the LDO token contract is processing a t

## Summary
Severity: Medium
Target: LDO
Loss: -
Attack method: False top-up
Published: 2023-09-10
Source: https://twitter.com/SlowMist_Team/status/1700782725593268448
Type: slowmist-incident

## Details
On September 10, according to on-chain intelligence from the SlowMist security team, when the LDO token contract is processing a transfer operation, if the transfer amount exceeds the amount actually held by the user, the operation will not trigger the rollback of the transaction. Instead, it will directly return a `false` as the processing result. This approach is different from many common ERC20 standard token contracts. Due to the above characteristics, there is a potential risk of "fake top-up", and malicious attackers may try to use this feature to conduct fraud. On September 11, Lido stated that this behavior was expected and complies with ERC20 token standards. LDO and stETH are still safe. The Lido Token Integration Guide will be updated with LDO details to show this more obviously.
