# [M] No ability to revoke restricted URI_SETTER role

## Summary
Severity: Medium
Reporter: dirk_y
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L53
Type: audit-issue

## Details
# No ability to revoke restricted URI_SETTER role

## Summary
The URI_SETTER role is the role given to an account that is allowed to set the base token URI. This role is not trusted, so there should be the ability to revoke the role from an account and assign the role to a new account.

## Vulnerability Detail
The URI_SETTER role is assigned to an account during contract creation in the `MeritNFT.sol` contract:

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

Because it has not been explicitly changed, the role admin for the URI_SETTER role is still the DEFAULT_ADMIN_ROLE. Because the DEFAULT_ADMIN_ROLE isn't assigned to an account during contract creation, nobody has the ability to add or revoke either of the roles.

This isn't relevant for the MINTER_ROLE because the minter role should only be given to the `MeritDutchAuction.sol` deployment, and if there were an issue during deployment time, the NFT could be redeployed at a new address. However, if the auction has already started and NFTs have been sold, then the NFT address now has inherent value and needs to be well protected. The fact that a restricted account with the URI_SETTER role could now modify the base token URI without consequence is a problem that should be resolved.

## Impact
A malicious or compromised account with the URI_SETTER can set the base token URI to an arbitrary and potentially malicious or inappropriate URL.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L53

## Tool used
Manual Review

## Recommendation
In order to prevent the minter role from being arbitrarily assigned to a new address after the auction has finished, the minter role and the uri setter role should have different admins, and the admin of the uri setter role should be assigned to another account that can revoke/add the role as necessary. In the below proposed change, the role admin is assigned to the contract creator but this could be changed to an explicit constructor argument:

```diff
diff --git a/dutch-nft/src/MeritNFT.sol b/dutch-nft/src/MeritNFT.sol
index bb862d0..8450e72 100644
--- a/dutch-nft/src/MeritNFT.sol
+++ b/dutch-nft/src/MeritNFT.sol
@@ -19,6 +19,8 @@ contract MeritNFT is ERC721Enumerable, AccessControlEnumerable {
     bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
     // Role for setting the baseURI
     bytes32 public constant URI_SETTER = keccak256("URI_SETTER");
+    // URI setter admin role
+    bytes32 public constant URI_SETTER_ADMIN = keccak256("URI_SETTER_ADMIN");
     // Prefix for the tokenURI. tokenURI = baseTokenURI + tokenId + .json
     string internal baseTokenURI_;
 
@@ -52,6 +54,9 @@ contract MeritNFT is ERC721Enumerable, AccessControlEnumerable {
         baseTokenURI_ = _baseTokenURI;
         _setupRole(URI_SETTER, _uriSetter);
         _setupRole(MINTER_ROLE, _minter);
+        _setupRole(URI_SETTER_ADMIN, msg.sender);
+
+        _setRoleAdmin(URI_SETTER, URI_SETTER_ADMIN);
     }
 
```
