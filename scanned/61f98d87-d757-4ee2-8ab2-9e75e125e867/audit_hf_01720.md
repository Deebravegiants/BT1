# [M] Manual Execution will not work with the current nonce implementation

## Summary
Severity: Medium
Contest weight: 0.4588
Dataset id: 9380
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When sending messages / tokens through CCIP, if the transaction fails on the destination chain, CCIP offers an option to manually execute (retry) the transaction again. One case where the transaction may fail is when the receiver contract on the destination blockchain reverted due to the gas limit being insufficient to execute the triggered function (Note: The gas limit value is set in the extraArgs param of the message) (Source: Chainlink Docs). In LaPoste.sol, when receiveMessage is successful, receivedNonce[chainId] is increased by message.nonce. The function also checks message.nonce <= receivedNonces[chainId].
```solidity
function receiveMessage(uint256 chainId, bytes calldata payload) external onlyAdapter {
    ILaPoste.Message memory message = abi.decode(payload, (ILaPoste.Message));
    // Check if the message has already been processed
    if (message.nonce <= receivedNonces[chainId]) revert MessageAlreadyProcessed();
    receivedNonces[chainId] += message.nonce;
    // ...
}
```
This nonce value is set when sending message, and it is incremented by one every time. Consider this scenario: Message 1 (with tokens locked on the source chain) is sent to the destination chain, message.nonce = 1, and receivedNonces[chainId]= 0. The check passes, the sender gets his minted tokens, and receivedNonces[chainId] is increased to 1. Message 2 (tokens locked on source chain) is sent to destination chain. message.nonce = 2, and receivedNonces[chainId]= 1. Something happened to the gas limit and this transaction reverts. Message 3 (tokens locked on source chain) is sent to destination chain. message.nonce = 3, and receivedNonces[chainId]= 1. Transaction passes and receivedNonces[chainId]= 3. Sender gets his minted tokens. Message 2 sender wants to retry his message through manual execution, but since message.nonce = 2, and receivedNonces[chainId]= 3, the function will always revert. The sender's token is locked on the source chain.

## Recommendation
One recommendation from the docs is to use EVMExtraArgsV2 with allowOutOfOrderExecution set to false so that the messaging order is sequential.
