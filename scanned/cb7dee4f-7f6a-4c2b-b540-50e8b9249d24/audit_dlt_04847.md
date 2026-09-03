# [H] Re-entrancy issue in ERC1155NFTProduct contract's mintByOwner function

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/110
Type: sherlock-finding

## Details
cryptphi

high

# Re-entrancy issue in ERC1155NFTProduct contract's mintByOwner function

## Summary
The mintByOwner function is vulnerable to re-entrancy attack due to the function making a call to ERC1155Upgradeable._mint()

## Vulnerability Detail
When the user or contract with the `MINT_ROLE` calls ERC1155NFTProduct.mintByOwner() , they are able to re-enter the function due to the call back in `_doSafeTransferAcceptanceCheck` in  the call to ERC1155Upgradeable._mint(). This would allow the Minter to re-enter mintByOwner multiple times. This would also cause some token totalSupply mismatch with balances.

## Impact
This would lead to a token totalSupply mismatch  and may lead to minting out a token by a user and possible a loss of funds in a corresponding context.

## Code Snippet
mintToCaller function with no re-entrancy protecton
```solidity
function mintByOwner(
        address account,
        uint256 id,
        uint256 amount,
        string memory tokenUri
    ) public onlyRole(MINT_ROLE) {
        require(!_exists(id), "NFT: token already minted");
        if (bytes(tokenUri).length > 0) {
            _tokenURIs[id] = tokenUri;
            emit URI(tokenUri, id);
        }
        _mint(account, id, amount, "");
        tokenSupply[id] += amount;
    }
```

## Tool used
Manual Review

## Recommendation

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/110_
