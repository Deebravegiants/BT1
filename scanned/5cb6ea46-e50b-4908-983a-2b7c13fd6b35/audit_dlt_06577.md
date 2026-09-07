# [M] Incorrect Data Type Handling in `writeVarInt` Function

## Summary
Severity: Medium
Chain: Smart contract
Component: illuminex
Published: 2024-07-03
Source: https://github.com/hats-finance/illuminex-0x0bb4aa1f58719707405c231fcdf0b405714799cf/issues/24
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x0fad636e222fe8446b48b613e8af237bc7fdfcce8e5c59d45c3d4c88501aa3a6
**Severity:** medium

**Description:**
**Description**\
There is a bug in the writeVarInt function of the Buffer.sol contract. The function incorrectly calls Endian.reverse32 with a uint16 argument instead of a uint32 argument. This can lead to incorrect data being written to the buffer and potential out-of-bounds errors.

**Attack Scenario**\
Describe how the vulnerability can be exploited.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
```
function writeVarInt(BufferIO memory buffer, uint256 value) internal pure {
        if (value <= 0xFC) {
            write(buffer, bytes.concat(bytes1(uint8(value))));
        } else if (value >= 253 && value <= 0xFFFF) {
            write(buffer, bytes.concat(bytes1(uint8(0xFD))));
            write(buffer, bytes.concat(bytes2(Endian.reverse16(uint16(value)))));
        } else if (value >= 65536 && value <= 0xFFFFFFFF) {
            write(buffer, bytes.concat(bytes1(uint8(0xFE))));
            write(buffer, bytes.concat(bytes4(Endian.reverse32(uint16(value)))));<------
        } else if (value >= 4_294_967_296 && value <= 0xFFFFFFFFFFFFFFFF) {
            write(buffer, bytes.concat(bytes1(uint8(0xFF))));
            write(buffer, bytes.concat(bytes8(Endian.reverse64(uint64(value)))));
        } else {
            revert("Value too large");
        }
    }
```
1. Allocate a buffer using the alloc function.
2. Attempt to write a variable integer  with a value between 65536 and 0xFFFFFFFF using the writeVarInt function.
3. Observe that the data written to the buffer is incorrect due to the improper handling of the data type.


_Trimmed to 38 lines — full report: https://github.com/hats-finance/illuminex-0x0bb4aa1f58719707405c231fcdf0b405714799cf/issues/24_
