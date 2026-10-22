# [M] Protocol will not work on ZkSync and Celo

## Summary
Severity: Medium
Contest weight: 0.4107
Dataset id: 9379
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Every chain contains a single version of LaPoste.sol, Adapter.sol, TokenFactory.sol. When a message is received, it assumes that LaPoste.sol shares the same address across all the chains:
```solidity
/// @notice Receives a message from another chain
/// @param message The received message
function ccipReceive(Client.Any2EVMMessage calldata message) external override onlyRouter {
    address source = abi.decode(message.sender, (address));
    if (source == address(0) || source != laPoste) revert InvalidSender();
    ILaPoste(laPoste).receiveMessage({chainId: getChainId(message.sourceChainSelector), payload: message.data});
}
```
However, ZkSync has different formula derivation, so it's impossible to deploy to the same address. Similar issues with Celo: it has different address derivation from seed phrase, it means create3 will result in a different address because the same tx sender can't be reproduced on Celo. The same goes vice versa: in the current design, LaPoste can't call Adapter on such a chain, because the adapter has a different address.

## Recommendation
Use specific addresses when sending messages to/from ZkSync and Celo.
