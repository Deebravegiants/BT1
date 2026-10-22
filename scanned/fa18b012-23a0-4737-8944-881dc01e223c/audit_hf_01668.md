# [H] Wallet initialize frontrun

## Summary
Severity: High
Contest weight: 0.5665
Dataset id: 9020
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deploy script does 2 transactions to deploy a wallet:
1. deploy contract
2. call initialize() (which accepts the first controller) (foundry, every call is a transaction)
```solidity
address _newWalletAddr = _factory.createProxy(_testWalletSalt);
Main(payable(_newWalletAddr)).initialize(deployer);
```
Wallet deployments can be tracked and awaited. An attacker can frontrun and call initialize() with malicious input.
One of the ideas:
1. Attacker frontruns, sets Controller=Attacker
2. Attacker updates implementation (Main.upgradeToAndCall()), to the malicious implementation
3. Sets back controller=TargetUser
4. The user keeps operation with this wallet, with the malicious implementation
5. Implementation has some malicious function to withdraw all tokens to the attacker. The attacker waits for some balance on the wallet, and invokes the attack function.

## Recommendation
Ensure the initialize() is called in the same transaction as the wallet deployment.
