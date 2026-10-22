# [M] receiveMessage() will revert when it runs out of gas

## Summary
Severity: Medium
Contest weight: 0.5631
Dataset id: 9381
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Protocol uses CCIP messaging in a strict way. It means that further messages per lane can't be processed until the execution of previous messages succeeds. As soon as any action can revert in LaPoste.receiveMessage(), further messages can't be processed. How an attacker can make his message revert. It uses try catch to execute a call to the attacker's contract:
```solidity
/// 2. Execute the message.
bool success;
if (message.payload.length > 0) {
    try IMessageReceiver(message.to).receiveMessage(chainId, message.sender, message.payload) {
        success = true;
    } catch {
        success = false;
    }
}
```
The problem is that try catch doesn't handle the out-of-gas error. So basically attacker can waste all gas in this external call, so that LaPoste.receiveMessage() always reverts. An attacker can perform such an attack on every CCIP lane so that any communication in LaPoste protocol will be DOSed. As a result, locked tokens on Mainnet will be locked forever, which means users lose money.

## Recommendation
Add executionGasLimit field to ILaposte.Message struct. And specify this gasLimit in external call here:
```solidity
/// 2. Execute the message.
bool success;
if (message.payload.length > 0) {
    try IMessageReceiver(message.to).receiveMessage{gas: message.executionGasLimit}(chainId, message.sender, message.payload) {
        success = true;
    } catch {
        success = false;
    }
}
```
