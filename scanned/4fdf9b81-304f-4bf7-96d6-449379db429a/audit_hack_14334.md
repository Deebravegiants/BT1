# [M] No validation to verify if the `_uriSetter` is set to the `zero` address in the constructor of the `MeritNFT` contract

## Summary
Severity: Medium
Reporter: blackhole
Source: https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritNFT.sol#L53
Type: audit-issue

## Details
# No validation to verify if the `_uriSetter` is set to the `zero` address in the constructor of the `MeritNFT` contract

## Summary

After the contract is deployed, it becomes impossible to update the `uriSetter` role.
If `_uriSetter` is set to `address(0)`, the `setBaseURI` function doesn't work, thereby preventing the admin from updating the `baseTokenURI` thereafter.


## Vulnerability Detail

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritNFT.sol#L53

```solidity
File: src/MeritNFT.sol#L45
    constructor(
        string memory _name,
        string memory _symbol,
        string memory _baseTokenURI,
        address _uriSetter, // @audit zero address check
        address _minter // @audit zero address check
    ) ERC721(_name, _symbol) {
        baseTokenURI_ = _baseTokenURI;
        _setupRole(URI_SETTER, _uriSetter);
        _setupRole(MINTER_ROLE, _minter);
    }

```

## Impact

If `_uriSetter` is set to a zero address, nobody can call the `setBaseURI` function.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritNFT.sol#L53
https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritNFT.sol#L67

## Tool used

Manual Review

## Recommendation

Recommend adding validation steps to check `_uriSetter` is set to 0 or not.

```solidity
File: src/MeritNFT.sol#L45
    constructor(
        string memory _name,
        string memory _symbol,
        string memory _baseTokenURI,
        address _uriSetter,
        address _minter
    ) ERC721(_name, _symbol) {
        baseTokenURI_ = _baseTokenURI;
        require(_uriSetter != address(0), "uriSetter error"); // @audit here
        _setupRole(URI_SETTER, _uriSetter);
        _setupRole(MINTER_ROLE, _minter);
    }

```
