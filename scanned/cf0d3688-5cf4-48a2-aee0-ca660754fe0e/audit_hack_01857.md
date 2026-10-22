# [C] Memory corruption in `Buffer`

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Although out of scope for this audit, the audit team noticed a memory corruption issue in the `Buffer` library. The `init` function is as follows:


**contracts/Buffer.sol:L22-L41**
```solidity
/**
* @dev Initializes a buffer with an initial capacity.
* @param buf The buffer to initialize.
* @param capacity The number of bytes of space to allocate the buffer.
* @return The buffer, for chaining.
*/
function init(buffer memory buf, uint capacity) internal pure returns(buffer memory) {
    if (capacity % 32 != 0) {
        capacity += 32 - (capacity % 32);
    }
    // Allocate space for the buffer data
    buf.capacity = capacity;
    assembly {
        let ptr := mload(0x40)
        mstore(buf, ptr)
        mstore(ptr, 0)
        mstore(0x40, add(32, add(ptr, capacity)))
    }
    return buf;
}
```

Note that memory is reserved only for `capacity` bytes, but the `bytes` actually requires `capacity + 32` bytes to account for the prefixed array length. Other functions in `Buffer` assume correct allocation and therefore corrupt nearby memory.

Although we didn't immediately spot an ENS exploit for this vulnerability, we consider any memory corruption issue to be important to address.

#### Example

A simple test shows the memory corruption issue:

```solidity
contract Test {
    using Buffer for Buffer.buffer;

    function test() external pure {
        Buffer.buffer memory buffer;
        buffer.init(1);

        // foo immediately follows buffer.buf in memory
        bytes memory foo = new bytes(0);
        
        assert(foo.length == 0);

        buffer.append("A");
 
        // "A" == 65, gets written to the high order byte of foo.length
        assert(foo.length == 65 * 256**31);
    }
}
```

#### Remediation

Allocate an additional 32 bytes as follows, to account for storing the `uint256` size of the `bytes` array:

```solidity
mstore(0x40, add(ptr, add(capacity, 32)))
```
