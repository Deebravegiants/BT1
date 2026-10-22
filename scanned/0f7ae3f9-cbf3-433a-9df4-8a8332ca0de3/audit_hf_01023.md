# [M] Missing type hash when hashing sub-struct breaks EIP-712 compliance

## Summary
Severity: Medium
Contest weight: 0.7095
Dataset id: 3783
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In SeaportProxy there is EIP-712 implementation with nested arrays of structs in the typed data which does not follow EIP-712.
Issue 1:
As stated in EIP-712 #Definition of encodeType:
If the struct type references other struct types (and these in turn reference even more struct types), then the set of referenced struct types is collected, sorted by name and appended to the encoding.
salt,bytes32 offerHash,bytes32 considerationHash) where offerHash and considerationHash are of types OfferItem[] and ConsiderationItem[], but are set as bytes32.
Issue 2:
Stated in EIP-712 #Definition of encodeData:
The array values are encoded as the keccak256 hash of the concatenated encodeData of their contents, with no delimiters between elements. The encoding depends on the size of the array elements.
As stated for the hashStruct:
The hashStruct function is defined as hashStruct(s : 𝕊) = keccak256(typeHash ‖ encodeData(s)) where typeHash = keccak256(encodeType(typeOf(s))).
Basically meaning the hash struct is the hashed concatenated value of the typehash and encoded data.
Having all this in mind the issue here is that when the sub-struct array items are hashed the type hash is missing:
```solidity
function hashOfferItem(OfferItem memory offerItem) internal view returns (bytes32) {
    return keccak256(
        abi.encode( // missing typehash
            offerItem.itemType,
            offerItem.token,
            offerItem.identifierOrCriteria,
            offerItem.startAmount,
            offerItem.endAmount
        )
    );
}
function hashConsiderationItem(ConsiderationItem memory considerationItem) internal view returns (bytes32) {
    return keccak256(
        abi.encode( // missing typehash
            considerationItem.itemType,
            considerationItem.token,
            considerationItem.identifierOrCriteria,
            considerationItem.startAmount,
            considerationItem.endAmount,
            considerationItem.recipient
        )
    );
}
```

## Recommendation
Change the Cancel type hash to appending both nested types in alphabetical order
```solidity
bytes32 constant CANCEL_TYPEHASH =
    keccak256(
        abi.encodePacked(
            "Cancel(bytes32 salt,OfferItem[] offerHash,ConsiderationItem[] considerationHash)",
            "OfferItem(uint8 itemType,address token,uint256 identifierOrCriteria,uint256 startAmount,uint256 endAmount)",
            "ConsiderationItem(uint8 itemType,address token,uint256 identifierOrCriteria,uint256 startAmount,uint256 endAmount,address recipient)"
        )
    );
```
Create type hashes for the offer item and consideration item structs
```solidity
bytes32 constant OFFER_ITEM_TYPE_HASH =
    keccak256(
        abi.encodePacked(
            "OfferItem(uint8 itemType,address token,uint256 identifierOrCriteria,uint256 startAmount,uint256 endAmount)"
        )
    );
bytes32 constant CONSIDERATION_ITEM_TYPE_HASH =
    keccak256(
        abi.encodePacked(
            "ConsiderationItem(uint8 itemType,address token,uint256 identifierOrCriteria,uint256 startAmount,uint256 endAmount,address recipient)"
        )
    );
```
Add type hash when hashing separate array items:
```solidity
function hashOfferItem(OfferItem memory offerItem) internal view returns (bytes32) {
    return keccak256(
        abi.encode(
            OFFER_ITEM_TYPE_HASH,
            offerItem.itemType,
            offerItem.token,
            offerItem.identifierOrCriteria,
            offerItem.startAmount,
            offerItem.endAmount
        )
    );
}
function hashConsiderationItem(ConsiderationItem memory considerationItem) internal view returns (bytes32) {
    return keccak256(
        abi.encode(
            CONSIDERATION_ITEM_TYPE_HASH,
            considerationItem.itemType,
            considerationItem.token,
            considerationItem.identifierOrCriteria,
            considerationItem.startAmount,
            considerationItem.endAmount,
            considerationItem.recipient
        )
    );
}
```
