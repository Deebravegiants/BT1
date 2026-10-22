# [M] Arrays hashed wrong when tokenizing breaks EIP-712

## Summary
Severity: Medium
Contest weight: 0.5735
Dataset id: 3789
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ColonyCollectibles::tokenize() function lets an admin tokenize a number of tokens for a given receiver/s. It implements EIP-712 signature verification to execute the mint.
The problem is the way the data for the digest is hashed. The tokenize function calls getTokenizeDigest which hashes the data as follows (where receivers and amounts are arrays):
```solidity
return MessageHashUtils.toEthSignedMessageHash(
    keccak256(
        abi.encodePacked(
            block.chainid,
            signerCounter,
            receivers,
            amounts,
            dbIdentifier
        )
    )
);
```
This is wrong because as stated in EIP-712: The array values are encoded as the keccak256 hash of the concatenated encodeData of their contents (i.e. the encoding of SomeType[5] is identical to that of a struct containing five members of type SomeType). Or in other words each array element has to be hashed separately before being added to the digest.

## Recommendation
Add functions that hash the elements of an array separately and call them from getTokenizeDigest
```solidity
function hashAddressArray(address[] memory receivers) internal pure returns (bytes32) {
    bytes32[] memory hashes = new bytes32[](receivers.length);
    for (uint256 i = 0; i < receivers.length; ++i) {
        hashes[i] = keccak256(abi.encode(receivers[i]));
    }
    return keccak256(abi.encodePacked(hashes));
}
function hashUintArray(uint256[] memory amounts) internal pure returns (bytes32) {
    bytes32[] memory hashes = new bytes32[](amounts.length);
    for (uint256 i = 0; i < amounts.length; ++i) {
        hashes[i] = keccak256(abi.encode(amounts[i]));
    }
    return keccak256(abi.encodePacked(hashes));
}
function getTokenizeDigest(
    address[] calldata receivers,
    uint256[] calldata amounts,
    uint64 dbIdentifier
) public view returns (bytes32) {
    return MessageHashUtils.toEthSignedMessageHash(
        keccak256(
            abi.encode(
                TOKENIZE_DIGEST_TYPEHASH,
                block.chainid,
                signerCounter,
                hashAddressArray(receivers),
                hashUintArray(amounts),
                dbIdentifier
            )
        )
    );
}
```
