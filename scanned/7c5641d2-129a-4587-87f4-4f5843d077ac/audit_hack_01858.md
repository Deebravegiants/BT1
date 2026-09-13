# [M] Overzealous resizing in `Buffer`

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

In the following code, the buffer is resized even when sufficient `capacity` is available to perform the write. The `buf.buf.length` term is unnecessary and leads to unnecessary resizing:


**contracts/Buffer.sol:L91-L95**
```solidity
function write(buffer memory buf, uint off, bytes memory data, uint len) internal pure returns(buffer memory) {
    require(len <= data.length);

    if (off + len > buf.capacity) {
        resize(buf, max(buf.capacity, len + off) * 2);
```

Contrast with the calculation in a similar function:


**contracts/Buffer.sol:L206-L209**
```solidity
function write(buffer memory buf, uint off, bytes32 data, uint len) private pure returns(buffer memory) {
    if (len + off > buf.capacity) {
        resize(buf, (len + off) * 2);
    }
```

#### Remediation

Check just the condition `if (off + len > buf.capacity)` when deciding whether to resize the buffer. This will be a significant gas savings in the common case of reserving exactly the right capacity and then performing two `append` operations.
