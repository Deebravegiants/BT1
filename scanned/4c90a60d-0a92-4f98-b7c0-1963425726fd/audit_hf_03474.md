# [M] Memory corruption in getBytes32FromBytes

## Summary
Severity: Medium
Contest weight: 0.7140
Dataset id: 18931
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `LibBytes` library is used to read and store `uint128` types compactly for Well functions. The function `getBytes32FromBytes()` will fetch a specific index as `bytes32`.

```solidity
/**
 * @dev Read the `i`th 32-byte chunk from `data`.
 */
function getBytes32FromBytes(bytes memory data, uint256 i) internal pure returns (bytes32 _bytes) {
    uint256 index = i * 32;
    if (index > data.length) {
        _bytes = ZERO_BYTES;
    } else {
        assembly {
            _bytes := mload(add(add(data, index), 32))
        }
    }
}
```

If the index is out of bounds in the data structure, it returns `ZERO_BYTES = bytes32(0)`. The issue is that the OOB check is incorrect. If `index=data.length`, the request is also OOB. For example: `data.length=0` -> array is empty, `data[0]` is undefined. `data.length=32` -> array has one `bytes32`, `data[32]` is undefined.

In other words, fetching the last element in the array will return whatever is stored in memory after the `bytes` structure.

## Proof of Concept
The damage is easily demonstrated using the example below:

```solidity
pragma solidity 0.8.17;

contract Demo {
    event Here();
    bytes32 private constant ZERO_BYTES = bytes32(0);

    function corruption_POC(bytes memory data1, bytes memory data2) external returns (bytes32 _bytes) {
        _bytes = getBytes32FromBytes(data1, 1);
    }

    function getBytes32FromBytes(bytes memory data, uint256 i) internal returns (bytes32 _bytes) {
        uint256 index = i * 32;
        if (index > data.length) {
            _bytes = ZERO_BYTES;
        } else {
            emit Here();
            assembly {
                _bytes := mload(add(add(data, index), 32))
            }
        }
    }
}
```

Calling corruption_POC with the following parameters:

```
{
	"bytes data1": "0x2222222222222222222222222222222222222222222222222222222222222222",
	"bytes data2": "0x3333333333333333333333333333333333333333333333333333333333333333"
}
```

The output `bytes32` is:

```
{
	"0": "bytes32: _bytes 0x0000000000000000000000000000000000000000000000000000000000000020"
}
```

The 0x20 value is in fact the size of the `data2` bytes that resides in memory from the call to `getBytes32FromBytes`.

## Recommendation
Change the logic to:

```solidity
if (index >= data.length) {
    _bytes = ZERO_BYTES;
} else {
    assembly {
        _bytes := mload(add(add(data, index), 32))
    }
}
```

The report is valid, but the function is not used in the code base and will be removed. Because of this, it was never tested and/or intended for use. Recommend medium.

The finding doesn’t impact code in scope in a way that would lead to loss of funds. Instead, it would affect only future code.

The function has been removed from the codebase.
