# [M] Mitigating security risks in the FairFundingToken contract

## Summary
Severity: Medium
Reporter: OCC
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/solidity/MintableERC721.sol#L7
Type: audit-issue

## Details
# Mitigating security risks in the FairFundingToken contract

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/solidity/MintableERC721.sol#L7

## Summary
1. There are no check if the caller of the function is authorized to mint tokens.
2. There are no checks for integer overflow. 
3. There are no validator for input data

## Vulnerability Detail
1. `mint` function has no requirment to check if the caller of the function is authorized to mint tokens.
2. The contract does not include any checks for integer overflow, which may result in unexpected behavior and could potentially be exploited by malicious one. 
3. The contract currently does not validate any input parameters, it may arise potential issues. 

## Impact
Medium

## Code Snippet
Manually review

## Tool used
Manually review

### Manual Review
Done

## Recommendation

Here's an updated version of the contract . 

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "@openzeppelin/contracts@4.8.1/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts@4.8.1/access/Ownable.sol";

contract FairFundingToken is ERC721, Ownable {
    constructor() ERC721("FairFundingToken", "FFT") {}

// to check if the caller of `mint() `has the minter role
    modifier onlyMinter() {
        require(msg.sender == owner() || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "FairFundingToken: must have minter role to mint tokens");
        _;
    }

    /**
     * @notice We expose `mint` and not `safeMint` here to avoid
     *         potential DoS issue when settling an auction.
     * @param to address of the token receiver
     * @param tokenId id to be minted
     */
    function mint(address to, uint256 tokenId) public onlyMinter {
       // To check if the receiver address is not the zero address.
        require(to != address(0), "FairFundingToken: cannot mint to the zero address");
        _mint(to, tokenId);
    }
    
 // To prevent transferring tokens to the contract itself 
    function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal override {
        super._beforeTokenTransfer(from, to, tokenId);
        require(to != address(this), "FairFundingToken: cannot transfer tokens to the contract itself");
    }
}

```
In the above, Added an `onlyMinter` modifier to check if the caller of the `mint` function has the minter role. This modifier checks if the caller is the contract owner or has a minter role assigned to them.

Added input validation to the mint function to check if the receiver address is not the zero address.

Added a check to the `_beforeTokenTransfer `function to prevent transferring tokens to the contract itself. This can prevent potential issues if the contract's code is updated or if the contract is replaced with a different contract.
