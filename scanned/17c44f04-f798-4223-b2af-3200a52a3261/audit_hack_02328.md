# [M] \[M09\] Not using OpenZeppelin contracts

## Summary
Severity: Medium
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/tree/v2.5.0
Type: audit-issue

## Details
[OpenZeppelin maintains a library of standard, audited, community-reviewed, and battle-tested smart contracts](https://github.com/OpenZeppelin/openzeppelin-contracts/tree/v2.5.0).  
Instead of always importing these contracts, the Holdefi project reimplements them in some cases, while in other cases it just copies them.

This increases the amount of code that the Holdefi team will have to maintain and misses all the improvements and bug fixes that the OpenZeppelin team is constantly implementing with the help of the community.

In particular, the following contracts and libraries are being reimplemented or copied:

* [the Ownable contract](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Ownable.sol) can be replaced with the [OpenZeppelin’s Ownable contract](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v2.5.0/contracts/ownership/Ownable.sol)
* [the SafeMath library](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/SafeMath.sol) can be replaced with the [OpenZeppelin’s SafeMath library](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v2.5.0/contracts/math/SafeMath.sol)
* The `ERC20` interface defined in [line 3](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/CollateralsWallet.sol#L3) of `CollateralsWallet.sol` and [line 25](https://github.com/holdefi/Holdefi/blob/f4df394d7cf6df347b1f1e9af8e2676c5933c2c9/contracts/Holdefi.sol#L25) of `Holdefi.sol` can be replaced with the [OpenZeppelin’s IERC20.sol interface](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v2.5.0/contracts/token/ERC20/IERC20.sol)

Consider importing the OpenZeppelin contracts instead of reimplementing or copying them. These contracts can be extended to add the extra functionalities required by Holdefi.  
Consider always using the full ERC interfaces so that obviously non-compliant implementations can be easily excluded.  
Consider updating the library to its [latest stable version for Solidity 0.5.16](https://github.com/OpenZeppelin/openzeppelin-contracts/tree/v2.5.0).

**Update**: _Not fixed. Holdefi’s statement for this issue:_

> If we use exactly OpenZeppelin contracts, we will miss some added features like ownerChanger. But we need them and can’t remove them. For ERC20 interface, we don’t need all functions so web just use a reduced version of IERC20.sol interface.

_We have updated our suggestion to make it clearer._
