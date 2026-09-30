# [M] EwmNftController is not strictly

## Summary
Severity: Medium
Contest weight: 0.7416
Dataset id: 1755
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Per the contest README:
The codebase expected to comply with the following EIPs
• Strictly compliant:
– EIP-4907 (rental standard for ERC721)
Per the EIP-4907 standard:
The supportsInterface method MUST return true when called with 0xad092b5c
However the interface IERC4907, inherited by EwmNftController, does not adhere to this
requirement. Because the EwmNftController is a rental NFT that is expected to follow the
EIP-4907 standard, this in turn breaks the rental NFT's compliance.
If a contract is in contest Scope, then all its parent contracts are included by
default.
The interfaceId of an interface/contract type is determined by XOR-ing all of their
function selectors together. The 0xad092b5c is the magic value that is the interfaceId of
IERC4907 defined in the standard:
https://eips.ethereum.org/EIPS/eip-4907
However, the current function signature/selector of setUser is as follow:
```solidity
function setUser(uint256 tokenId, address user) external;
```
ontracts/interfaces/IERC4907.sol#L15
Which is different from the 4907 standard, having an extra expires parameter:
```solidity
function setUser(uint256 tokenId, address user, uint64 expires) external;
```
causing the interfaceId to become different. Then it is impossible for supportInterface
to return true for the interface ID 0xad092b5c.
ontracts/EwmNftController.sol#L211-L213
Internal pre-conditions
None
External pre-conditions
None
Attack Path
N/A
Non-compliance with the ERC-4907 standard which the protocol expects strictly.
Smart contract integration issues may also arise for contracts interacting with the NFT
and expecting strict interface support, given that the NFT holders are meant to be EWM
Light Client runners, which can be expected to be smart contract users, as opposed to
regular app users.

## Proof of Concept
The following test, when run on Remix IDE, will yield a different value for type(IERC4907).interfaceId than the standard. Replacing it with the correct interface will also yield the
correct interfaceId
```solidity
// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.0;
// copy pasted from contest repo
interface IERC4907 {
    // Logged when the user of a token assigns a new user or updates expires
    /// @notice Emitted when the `user` of an NFT or the `expires` of the `user` is changed
    event UpdateUser(uint256 indexed tokenId, address indexed user, uint64 expires);
    /// @notice set the user and expires of a NFT
    /// @dev The zero address indicates there is no user
    /// Throws if `tokenId` is not valid NFT
    /// @param user The new user of the NFT
    function setUser(uint256 tokenId, address user) external;
    /// @notice Get the user address of an NFT
    /// @dev The zero address indicates that there is no user or the user is expired
    /// @param tokenId The NFT to get the user address for
    /// @return The user address for this NFT
    function userOf(uint256 tokenId) external view returns (address);
    /// @notice Get the user expires of an NFT
    /// @dev The zero value indicates that there is no user
    /// @param tokenId The NFT to get the user expires for
    /// @return The user expires for this NFT
    function userExpires(uint256 tokenId) external view returns (uint64);
}
contract Test {
    function testInterfaceId() public pure returns(bytes4){
        return type(IERC4907).interfaceId; // 0x96745459
    }
}
```

## Recommendation
The function setUser should include a (possibly empty) expiry parameter to match the
correct interface.
