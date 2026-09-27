# [M] 7.2 Description of toBoolean() Is Incorrect

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

In RLPReader, the description of toBoolean() states that "any non-zero byte is considered true". The
function takes an RLPItem as input.

In RLP encoding, byte values in the range [0x80-0xff] are encoded as 2 bytes like this:
[0x81, the_byte]. For RLPItems encoding such values, toBoolean() will revert, since it enforces
that the length of the RLPItem is 1. This is a mismatch, as these values are non-zero and should return
true according to the comment.

Specification changed:

The comment has been changed to:

```
// any non-zero byte < 128 is considered true
```
