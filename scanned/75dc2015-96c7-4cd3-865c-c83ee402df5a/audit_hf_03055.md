# [M] `RuniverseLand.sol#mint`

## Summary
Severity: Medium
Contest weight: 0.2690
Dataset id: 17242
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[contracts/RuniverseLand.sol#L77](https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/dcad1802bf258bf294900a08a03ca0d26d2304f4/contracts/RuniverseLand.sol#L77)  
[contracts/RuniverseLand.sol#L101](https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/dcad1802bf258bf294900a08a03ca0d26d2304f4/contracts/RuniverseLand.sol#L101)

The `mint()` function uses `numMinted` to generate the `tokenId`:
    
    File: RuniverseLand.sol
    72:     function mint(address recipient, PlotSize size)
    73:         public
    74:         override
    75:         returns (uint256)
    76:     {
    77:         uint256 tokenId = numMinted;
    78:         mintTokenId(recipient, tokenId, size);
    79:         return tokenId;
    80:     }

This `numMinted` value corresponds to the `totalSupply()`:
    
    File: RuniverseLand.sol
    145:     function totalSupply() public view returns (uint256) {
    146:         return numMinted;
    147:     }

However, the `mintTokenId()` function can be called with any `tokenId`:
    
    File: RuniverseLand.sol
    088:     function mintTokenId(
    089:         address recipient,
    090:         uint256 tokenId,
    091:         PlotSize size
    092:     ) public override nonReentrant {
    093:         require(numMinted < MAX_SUPPLY, "All land has been minted");
    094:         require(
    095:             _msgSender() == primaryMinter || _msgSender() == secondaryMinter,
    096:             "Not a minter"
    097:         );
    098:         numMinted += 1;
    099:         emit LandMinted(recipient, tokenId, size);
    100:         
    101:         _mint(recipient, tokenId);
    102:     }

Imagine the following scenario:

  * The contracts just got deployed and `numMinted == 0`
  * `primaryMinter` calls `mintTokenId()` with `tokenId == 1`

    * Now `numMinted == 1`
  * `secondaryMinter` calls `mint()`

    * In this case, `tokenId == numMinted`
    * `_mint()` gets called with `tokenId == 1` which already exists, so it fails

## Recommendation
Given that `RuniverseLand.sol#mint()` isn’t called in `RuniverseLandMinter`, I feel like it should simply be deleted.  
`primaryMinter` or `secondaryMinter` can simply call `mintTokenId()` directly.

Valid concern based on external requirements + the fact that arbitrary data can be inputted.

The warden has shown an inconsistency in using `mint` and `mintTokenId` which can cause the bricking of the minting functionality.

Because this is an undesirable scenario which can happen via ordinary operations, I agree with Medium Severity.

We updated the code with the next changes:  

  * We removed mint method from interface and contract

<https://github.com/bisonic-official/plot-contract/commit/ea8abd7faffde4218232e22ba5d8402e37d96878>
