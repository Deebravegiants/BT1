# [H] Contracts never initialize owner for Ownable.sol

## Summary
Severity: High
Reporter: 0xpinky
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/4d4a509b1f8e521583d82c042ef4bce919fe8e12/contracts/access/Ownable.sol#L38-L40
Type: audit-issue

## Details
# Contracts never initialize owner for Ownable.sol

## Summary
OZ's `Ownable.sol` now requires the owner to be explicitly set rather than assuming msg.sender as before. Since the contracts never call the `Ownable.sol` constructor _owner is never set and is left as address(0). This makes MeritDutchAuction.sol completely nonfunctional and disables all owner realated functions.

## Vulnerability Detail

Following OZ version is found in the package.jason

```solidity
{
  "dependencies": {
    "@openzeppelin/contracts": "^4.9.2"
  }
}
```

But, when we look at the OZ latest ownable, the constructor takes input argument which is set as owner.

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/4d4a509b1f8e521583d82c042ef4bce919fe8e12/contracts/access/Ownable.sol#L38-L40

The Ownable.sol (inherited by Ownable2Step.sol) constructor now requires the owner to be explicitly set rather than always defaulting to msg.sender.

## Impact

Non function of `onlyOwner` modifier protection.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87

## Tool used

Manual Review

## Recommendation
Call the Ownable.sol constructor to set the owner
