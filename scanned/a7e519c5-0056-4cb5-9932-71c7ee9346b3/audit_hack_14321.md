# [H] In MeritNFT.sol, roles will not be able to set due to _setupRole() deprecation and non-existence

## Summary
Severity: High
Reporter: MohammedRizwan
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/package.json#L3
Type: audit-issue

## Details
# In MeritNFT.sol, roles will not be able to set due to _setupRole() deprecation and non-existence

## Summary
In MeritNFT.sol, roles will not be able to set due to _setupRole() deprecation and non-existence.

## Vulnerability Detail

## Impact

In MeritNFT.sol, the constructor is used to set different roles by _setupRole()

```solidity
File: dutch-nft/src/MeritNFT.sol

45    constructor(
46        string memory _name,
47       string memory _symbol,
48        string memory _baseTokenURI,
49        address _uriSetter,
50        address _minter
51    ) ERC721(_name, _symbol) {
52        baseTokenURI_ = _baseTokenURI;
53        _setupRole(URI_SETTER, _uriSetter);
54        _setupRole(MINTER_ROLE, _minter);
55    }
```

The major issue here is constructor has used _setupRole() function to set the different roles and it calls this function from openzeppelin library but _setupRole() has been deprecated and the openzeppelin library don't have a _setupRole() in version 4.9.2 which is the [latest version](https://github.com/OpenZeppelin/openzeppelin-contracts/releases) of openzeppelin library as used by the MeritNFT.sol contracts.

Openzeppelin version is verified from package.json,

```

{
  "dependencies": {
    "@openzeppelin/contracts": "^4.9.2"
  }
}
```
[Reference link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/package.json#L3)

Both [AccessControlEnumerable.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/AccessControlEnumerable.sol) and [AccessControl.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/AccessControl.sol) does not have _setupRole functions.

Therefore while using _setupRole() in constructor it will not set the roles as given in constructor parameters because constructor will not be able to fetch _setupRole() from openzeppelin library and the contract will not be able to set the roles. **This means that onlyMinter and onlyUriSetter modifier will not be able to work in contract.**

```solidity

modifier onlyMinter {
```

```solidity

modifier onlyUriSetter {
````

_setupRole() existence further checked in interfaces in [IAccessControl.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/IAccessControl.sol) and [IAccessControlEnumerable.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/IAccessControlEnumerable.sol) but as confirmed it is deprecated and does not exist in interfaces too.

**_setupRole() is deprecated in favor of _grantRole() and _setupRole() does not exist in openzeppelin contracts, See below reference link**
[Reference link](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3489/files)

**Therefore To mitigate this issue, Recommend to use _grantRole().**

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritNFT.sol#L53-L54

## Tool used
Manual Review

## Recommendation
Use _grantRole() in constructor.

```solidity

    constructor(
        string memory _name,
        string memory _symbol,
        string memory _baseTokenURI,
        address _uriSetter,
        address _minter
    ) ERC721(_name, _symbol) {
        baseTokenURI_ = _baseTokenURI;
-        _setupRole(URI_SETTER, _uriSetter);
+        _grantRole(URI_SETTER, _uriSetter);

-        _setupRole(MINTER_ROLE, _minter);
+        _grantRole(MINTER_ROLE, _minter);
    }
```
