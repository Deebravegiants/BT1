# [M] OpenZeppelin Contracts base64 encoding may read from potentially dirty memory

## Summary
Severity: Medium
Chain: Solidity
Component: @openzeppelin/contracts
CVE: CVE-2024-27094
CWE: Out-of-bounds Read
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-9vx6-7xxf-x967
Type: github-advisory

## Details
### Impact

The `Base64.encode` function encodes a `bytes` input by iterating over it in chunks of 3 bytes. When this input is not a multiple of 3, the last iteration may read parts of the memory that are beyond the input buffer.

Although the `encode` function pads the output for these cases, up to 4 bits of data are kept between the encoding and padding, corrupting the output if these bits were dirty (i.e. memory after the input is not 0). These conditions are more frequent in the following scenarios:

- A `bytes memory` struct is allocated just after the input and the first bytes of it are non-zero.
- The memory pointer is set to a non-empty memory location before allocating the input.

Developers should evaluate whether the extra bits can be maliciously manipulated by an attacker.

### Patches

Upgrade to 5.0.2 or 4.9.6.

### References

This issue was reported by the Independent Security Researcher Riley Holterhus through Immunefi (@rileyholterhus on X)
