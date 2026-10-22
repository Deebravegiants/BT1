# [M] ERC1155Bridgable is not EIP-1155

## Summary
Severity: Medium
Contest weight: 0.5941
Dataset id: 23233
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the README:
The Bridged1155 should be strictly compliant with EIP-1155 and EIP-2981
EIP-1155 states the following about ERC1155Metadata_URI extension:
The optional ERC1155Metadata_URI extension can be identified with the ERC-165 Standard Interface Detection.
If the optional ERC1155Metadata_URI extension is included:
• The ERC-165 supportsInterface function MUST return the constant value true if 0x0e89341c is passed through the interfaceID argument.
• Changes to the URI MUST emit the URI event if the change can be expressed with an event (i.e. it isn't dynamic/programmatic).
But we see that:
• ERC1155Bridgable does support the extension, and returns the required constant via supportsInterface
• It does not emit the URI event as required, when it's changed via function setTokenURIAndMintFromRiftAbove:
```solidity
function setTokenURIAndMintFromRiftAbove(uint _id, uint _amount, string memory _uri, address _recipient) external {
    if (msg.sender != INFERNAL_RIFT_BELOW) {
        revert NotRiftBelow();
    }
    // Set our tokenURI
    uriForToken[_id] = _uri;
    // Mint the token to the specified recipient
    _mint(_recipient, _id, _amount, '');
}
```
Notice that when bridging the ERC-1155 tokens, URIs are retrieved from the corresponding token contract by InternalRiftAbove, and encoded into the package as follows:
```solidity
// Go through each NFT, set its URI and escrow it
uris = new string[](numIds);
for (uint j; j < numIds; ++j) {
    // Ensure we have a valid amount passed (TODO: Is this needed?)
    tokenAmount = params.amountsToCross[i][j];
    if (tokenAmount == 0) {
        revert InvalidERC1155Amount();
    }
    uris[j] = erc1155.uri(params.idsToCross[i][j]);
    erc1155.safeTransferFrom(msg.sender, address(this), params.idsToCross[i][j], params.amountsToCross[i][j], '');
}
// Set up payload
package[i] = Package({
    chainId: block.chainid,
    collectionAddress: collectionAddress,
    ids: params.idsToCross[i],
    amounts: params.amountsToCross[i],
    uris: uris,
    royaltyBps: _getCollectionRoyalty(collectionAddress, params.idsToCross[i][0]),
    name: '',
    symbol: ''
});
```
I.e. the information is properly retrieved, transferred, and is available; but the URI event is not emitted as required; this breaks the specification.
Protocols integrating with ERC1155Bridgable may work incorrectly.

## Recommendation
Compare the URI supplied for an NFT in function setTokenURIAndMintFromRiftAbove, and if it has changed -- emit the URI event as required per the specification.
