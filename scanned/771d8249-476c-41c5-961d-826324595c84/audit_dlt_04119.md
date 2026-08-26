# [M] flashAction and _releaseToAddress function transfers NFT without any address check

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/289
Type: sherlock-finding

## Details
Sm4rty

medium

# flashAction and _releaseToAddress function transfers NFT without any address check

## Summary
flashAction and _releaseToAddress function in CollateralToken contract transfers NFT without any address check

## Vulnerability Detail
There is no check if the reciever address for the nft can handle nft in flashAction and _releaseToAddress function in CollateralToken contract . There should exist a check for if reciever is not zero address.
Check //@audit tag in code below for more details.
Here in  releaseToAddress function, _releaseToAddress is called and NFT is transferred to releaseTo address. Which has a public visibility and can be called by anyone. And no address check is present here.

## Impact
There is no zero address check for the beneficiary ,therefore it is possible the beneficiary is zero and nft can be lost


## Code Snippet
[Like to code](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/CollateralToken.sol#L204-L227)
```solidity
  function releaseToAddress(uint256 collateralId, address releaseTo)
    public
    releaseCheck(collateralId)
  {
    //check liens
    require(
      msg.sender == ownerOf(collateralId),
      "You don't have permission to call this"
    );
    _releaseToAddress(collateralId, releaseTo); // @audit Here _releaseToAddress is called and NFT is transferred to releaseTo address. Which has a public visibility and can be called by anyone. And no address check is present here.
  }

  /**
   * @dev Transfers locked collateral to a specified address and deletes the reference to the CollateralToken for that NFT.
   * @param collateralId The ID for the CollateralToken of the NFT to unlock.
   * @param releaseTo The address to send the NFT to.
   */
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/289_
