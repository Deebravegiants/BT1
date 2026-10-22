# [H] Function token() of cloneERC1155ERC20Pair() reads from wrong location

## Summary
Severity: High
Contest weight: 0.6013
Dataset id: 15676
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function token() loads the token data from position 81. However on ERC1155 pairs it should load it from position 93. Currently, it doesn't retrieve the right values and the code won't function correctly.
```solidity
LSSVMPair.sol:
_factory := shr(0x60, calldataload(sub(calldatasize(), paramsLength)))

LSSVMPair.sol:
_bondingCurve := shr(0x60, calldataload(add(sub(calldatasize(), paramsLength), 20)))

LSSVMPair.sol:
_nft := shr(0x60, calldataload(add(sub(calldatasize(), paramsLength), 40)))

LSSVMPair.sol:
_poolType := shr(0xf8, calldataload(add(sub(calldatasize(), paramsLength), 60)))

LSSVMPairERC1155.sol: id := calldataload(add(sub(calldatasize(), paramsLength), 61))

LSSVMPairERC721.sol:
_propertyChecker := shr(0x60, calldataload(add(sub(calldatasize(), paramsLength), 61)))

LSSVMPairERC20.sol:
_token := shr(0x60, calldataload(add(sub(calldatasize(), paramsLength), 81)))

function cloneERC1155ERC20Pair(...) ... {
    assembly {
        mstore(add(ptr, 0x3e), shl(0x60, factory)) // position 0 - 20 bytes
        mstore(add(ptr, 0x52), shl(0x60, bondingCurve)) // position 20 - 20 bytes
        mstore(add(ptr, 0x66), shl(0x60, nft)) // position 40 - 20 bytes
        mstore8(add(ptr, 0x7a), poolType) // position 60 - 1 bytes
        mstore(add(ptr, 0x7b), nftId) // position 61 - 32 bytes
        mstore(add(ptr, 0x9b), shl(0x60, token)) // position 93 - 20 bytes
    }
}
```

## Recommendation
After the review has started, the function token() has been updated to read the last 20 bytes. See PR#21.
