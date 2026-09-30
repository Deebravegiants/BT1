# [H] InfernalRiftBelow.claimRoyalties

## Summary
Severity: High
Contest weight: 0.8767
Dataset id: 23214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
claimRoyalties used to accept the message on the L1, then execute ERC721Bridgable.claimRoyalties, but not the authentication callers, may result in the loss of the assets in the protocol.
claimRoyalties are used to accept cross-chain calls, but msg.sender is not validated:
```solidity
if (ICrossDomainMessenger(msg.sender).xDomainMessageSender() !=
INFERNAL_RIFT_ABOVE) {
    revert CrossChainSenderIsNotRiftAbove();
}
```
If msg.sender is a contract account implementing the ICrossDomainMessenger interface, the xDomainMessageSender function returns an address of INFERNAL_RIFT_ABOVE, which means that the claimRoyalties function can be invoked.
So anyone can call this function as long as he deploys a contract.
InfernalRiftBelow.claimRoyalties function will be called ERC721Bridgable.claimRoyalties, transfer NFTs from ERC721Bridgable contract, so any can transfer NFTs from ERC721Bridgable.
L1 Send message to L2:
```solidity
function claimRoyalties(address _collectionAddress, address _recipient, address[]
calldata _tokens, uint32 _gasLimit) external {
    .....
    ICrossDomainMessenger(L1_CROSS_DOMAIN_MESSENGER).sendMessage(
        INFERNAL_RIFT_BELOW,
        abi.encodeCall(
            IInfernalRiftBelow.claimRoyalties,
            (_collectionAddress, _recipient, _tokens)
        ),
        _gasLimit
    );
    emit RoyaltyClaimStarted(address(INFERNAL_RIFT_BELOW), _collectionAddress,
    _recipient, _tokens);
}
```
Anyone can steal NFT from the protocol.

## Recommendation
```solidity
if (msg.sender != L2_CROSS_DOMAIN_MESSENGER) {
    revert NotCrossDomainMessenger();
}
```
