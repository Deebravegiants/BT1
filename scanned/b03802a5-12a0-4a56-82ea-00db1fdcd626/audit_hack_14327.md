# [H] The auction will not work as intended as no address has the `MINTER_ROLE`

## Summary
Severity: High
Reporter: sorrynotsorry
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63
Type: audit-issue

## Details
# The auction will not work as intended as no address has the `MINTER_ROLE`

## Summary
The auction will not work as intended as no address has the `MINTER_ROLE` 
## Vulnerability Detail
`MeritNFT`'s `mint` function has `onlyMinter` modifier in order to mint the tokens.
Accordingly the `MINTER_ROLE` is assigned to `_minter` at the `constructor` via an input parameter.
As per the contracts, it's understood that MeritNFT contract is deployed first since the auction contract has a setter to set the MeritNFT contract address.

And MeritNFT doesn't have any setter function that can assign the MINTER_ROLE since `_grantRole` function of `AccessControlEnumerable` is an internal function and should be called via an other function inside the MeritNFT contract
## Impact
The contracts will not work as designed and there will be no NFT minted via `MeritDutchAuction.mint()`

## Code Snippet

```solidity
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _mint(_receiver, _tokenId);
    }
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63)

```solidity
    constructor(
        string memory _name,
        string memory _symbol,
        string memory _baseTokenURI,
        address _uriSetter,
        address _minter
    ) ERC721(_name, _symbol) {
        baseTokenURI_ = _baseTokenURI;
        _setupRole(URI_SETTER, _uriSetter);
        _setupRole(MINTER_ROLE, _minter);
    }
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L45-L55)

```solidity
    /// @notice Sets the NFT contract address, can only be called once, only calable by owner
    /// @param nft_ Address of the NFT contract
    function setNFT(address nft_) external onlyOwner {
        // Can only be set once
        require(address(nft) == address(0), "NFT already set");
        // NFT contract must allow this contract to mint NFTs
        nft = MeritNFT(nft_);
    }
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L89-L96)
## Tool used

Manual Review

## Recommendation
Implement a setter function for internally calling  `AccessControlEnumerable._grantRole()` to pass at least the `MINTER_ROLE`
