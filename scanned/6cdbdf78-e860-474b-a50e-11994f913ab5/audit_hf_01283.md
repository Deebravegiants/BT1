# [M] ERC1967Factory: Unsafe memory pointer allocation

## Summary
Severity: Medium
Contest weight: 0.2192
Dataset id: 6044
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ERC1967Factory contract the _initCode function is responsible for allocating memory and for writing the deployment bytecode for proxies to memory. In an effort to save gas the function does not adjust the memory pointer to indicate that the section of memory storing the bytecode is now in use.
Not only is this not memory safe, creating a pointer to memory that may be reallocated/used by other parts of the code can lead to bugs if a developer attempts to inherit from and use the ERC1967Factory contract and subsequently implicitly allocates some memory.
Standalone the ERC1967Factory contract seems to be correct, however, this issue is still relevant because there's no indication to potential users of the Solady library that the ERC1967Factory.sol:ERC1967Factory contract is not intended for 3rd party use. The ﬁle sits under the library's src/utils/ folder along with other libraries intended for use by library consumers & does not have any comments directly indicating that it's not for consumption by library users.
Beyond being unsafe the _initCode function also violates Solidity's conventions. Typically bytes memory pointers in Solidity are expected to point to a word of memory storing the length of the data directly followed by the data itself. The memory pointer created by the _initCode directly points to a static piece of data, offset by 19 bytes and not having any length.

## Recommendation
If the ERC1967Factory contract is intendend solely for standalone use & deployment as an on-chain component. Add comments reﬂecting this fact and move the ﬁle to its own folder with a name such as standalone or component denoting that it's different from the libraries intended for direct use and integration with the contracts of 3rd parties.
Furthermore, use a more "neutral" datatype such as uint256/bytes32 or even a custom type for the return value from the _initCode function to indicate that it's not a normal memory pointer.
If intended for 3rd party use ensure the _initCode function updates the free memory pointer to reﬂect its reserved memory area. Furthermore ensure that the return bytes memory value follows Solidity's conventions, pointing to a word with the data's length followed by the data itself.
