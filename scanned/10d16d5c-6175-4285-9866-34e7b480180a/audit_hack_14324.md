# [M] Role modification feature is broken

## Summary
Severity: Medium
Reporter: IllIllI
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/a55af77c75e8e5ce5205d2787856ee52055adf11/contracts/access/AccessControl.sol#L39-L57C29
Type: audit-issue

## Details
# Role modification feature is broken

## Summary

Once the initial minter and URI setter addresses are assigned, no other addresses can be given these roles


## Vulnerability Detail

No address is ever assigned the [DEFAULT_ADMIN_ROLE](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/a55af77c75e8e5ce5205d2787856ee52055adf11/contracts/access/AccessControl.sol#L39-L57C29), so no address, including the deployer, is able to give other addresses roles once the NFT has been constructed.


## Impact

The project could have easily just had two immutable addresses, and verified that the caller was one of the respective addresses for each permissioned function. Instead, the project uses [AccessControlEnumerable](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L10), which indicates that the project wishes to be able to change which addresses have these roles, and to perhaps (in the case of the URI_SETTER role) have multiple addresses have these roles.

During construction, the NFT is given a `baseTokenURI_`, but in order to have a blind mint, it's likely that the URI will be set to some default value, but changed later after the auction is complete. If another user needs to be given a role (e.g. the old role holder got fired) after the mint has completed (which can be indefinitely long), this can't be done. The only change that can be made to roles is for the current role holder to renounce it themselves. I believe these roles will be given to individual game developer companies who wish to use the Beam middleware, so being able to change an address' roles is important.


## Code Snippet

The two users are given their roles in the constructor, but nobody is given the `DEFAULT_ADMIN_ROLE` role:
```solidity
// File: src/MeritNFT.sol : MeritNFT.constructor()   #1

45        constructor(
46            string memory _name,
47            string memory _symbol,
48            string memory _baseTokenURI,
49            address _uriSetter,
50            address _minter
51        ) ERC721(_name, _symbol) {
52            baseTokenURI_ = _baseTokenURI;
53 @>         _setupRole(URI_SETTER, _uriSetter);
54 @>         _setupRole(MINTER_ROLE, _minter);
55:       }
```
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L45-L55

Only the [minter](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63
) and only the [URI setter](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L67-L69
) role member can mint and change the base URI, respectively.


## Tool used

Manual Review


## Recommendation

Call `_grantRole(DEFAULT_ADMIN_ROLE, msg.sender);` in the constructor
