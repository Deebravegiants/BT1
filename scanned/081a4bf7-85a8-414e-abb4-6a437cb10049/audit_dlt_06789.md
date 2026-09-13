# [M] Assets in a Safe can be lost

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-01-renft
Published: 2024-01-18
Source: https://github.com/code-423n4/2024-01-renft-findings/issues/323
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/src/policies/Guard.sol#L195-L293


# Vulnerability details

## Impact
The `Guard.sol` contract is enabled on Safe's and uses the [`_checkTransaction`](https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/src/policies/Guard.sol#L195-L293) function to ensure that transactions that the Safe executes do not transfer the asset out of the Safe.

The `checkTransaction` function achieves this by isolating the function selector and checking that it is not a disallowed function selector. For instance: `safeTransferFrom`, `transferFrom`, `approve`, `enableModule`, etc.

The list does not, however, check for calls to `burn` the token, neither does it check if it is a `permit`. The sponsor has noted the following: 

> The
[Guard](https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/src/policies/Guard.sol) contract can only protect against the transfer of tokens that faithfully
implement the ERC721/ERC1155 spec

But this does not acknowledge the fact that an ERC721/ERC1155 implementation can still be an honest implementation and have extra functionality. In particular, the `burn` function is a common addition to many ERC721 contracts, usually granted through inheriting `ERC721Burnable`.

For example, the following projects all have a `burn` function, and Safe's protected by `Guard.sol` that hold these NFTs will be vulnerable to loss of assets via a malicious renter:
- [Pudgy Penguins](https://etherscan.io/address/0xbd3531da5cf5857e7cfaa92426877b022e612cf8#writeContract)  
- [Lil Pudgies](https://etherscan.io/address/0x524cab2ec69124574082676e6f654a18df49a048#writeContract)
- [Oh Ottie](https://etherscan.io/address/0x7ff5601b0a434b52345c57a01a28d63f3e892ac0#code#F3#L45)

These are three that are in the top 10 projects on Opensea at the time of writing. 

## Proof of Concept
We can see in the `Guard.sol` file that certain function selectors are imported to be tested against:
```
import {
    shared_set_approval_for_all_selector,
    e721_approve_selector,
    e721_safe_transfer_from_1_selector,
    e721_safe_transfer_from_2_selector,
    e721_transfer_from_selector,
    e721_approve_token_id_offset,
    e721_safe_transfer_from_1_token_id_offset,
    e721_safe_transfer_from_2_token_id_offset,
    e721_transfer_from_token_id_offset,
    e1155_safe_transfer_from_selector,
    e1155_safe_batch_transfer_from_selector,
    e1155_safe_transfer_from_token_id_offset,
    e1155_safe_batch_transfer_from_token_id_offset,
    gnosis_safe_set_guard_selector,
    gnosis_safe_enable_module_selector,
    gnosis_safe_disable_module_selector,
    gnosis_safe_enable_module_offset,
    gnosis_safe_disable_module_offset
} from "@src/libraries/RentalConstants.sol";
```  

From the `_checkTransaction` function we see that there is no check for `burn`, `burnFrom` or `permit`.

A malicious renter who is renting the asset can still execute `burn` (common), `burnFrom` (rare) or `permit` (popularized by [Uni v3](https://github.com/Uniswap/v3-periphery/blob/697c2474757ea89fec12a4e6db16a574fe259610/contracts/base/ERC721Permit.sol#L52C9-L86)), which will lead to loss of the asset.  

## Coded PoC  


The below test can be placed in the `CheckTransaction.t.sol` test file. It should be run with `forge test --match-test test_PoC -vvvv`

```
    function test_PoC() public {
        bytes4 burn_selector = 0x42966c68;
        // Create a rentalId array
        RentalAssetUpdate[] memory rentalAssets = new RentalAssetUpdate[](1);
        rentalAssets[0] = RentalAssetUpdate(
            RentalUtils.getItemPointer(address(alice.safe), address(erc721s[0]), 0),
            1
        );

        // Mark the rental as actively rented in storage
        _markRentalsAsActive(rentalAssets);

        // Build up the `transferFrom(address from, address to, uint256 tokenId)` calldata
        bytes memory burnCalldata = abi.encodeWithSelector(
            burn_selector,
            69
        );

        // Expect revert because of an unauthorized function selector
        _checkTransactionRevertUnauthorizedSelector(
            address(alice.safe),
            address(erc721s[0]),
            burn_selector,
            burnCalldata
        );
    }
```

The console output is:  
```
Encountered 1 failing test in test/unit/Guard/CheckTransaction.t.sol:Guard_CheckTransaction_Unit_Test
[FAIL. Reason: call did not revert as expected] test_PoC() (gas: 96093)
```

This shows that the `checkTransaction` would not protect against calls to `burn` the asset.

## Tools Used  
Manual review

## Recommended Mitigation Steps  
Although not a catch-all, adding checks for `burn`, `burnFrom` and `permit` functions (which are common in smart contracts) should prevent this in most cases.

Selectors:  
- `burn`: `0x42966c68`
- `burnFrom`: `0x1fe41211`  
- `permit` : `0xabae8f0d`

In the `Guard.sol` file:  
```diff  
        } else if (selector == e1155_safe_transfer_from_selector) {
            // Load the token ID from calldata.
            uint256 tokenId = uint256(
                _loadValueFromCalldata(data, e1155_safe_transfer_from_token_id_offset)
            );

            // Check if the selector is allowed.
            _revertSelectorOnActiveRental(selector, from, to, tokenId);
+       } else if (selector == burn_selector) {
+           // Load the extension address from calldata.
+           address extension = address(
+               uint160(
+                    uint256(
+                       _loadValueFromCalldata(data, burn_selector_offset)
+                   )
+               )
+           );
+
+            _revertSelectorOnActiveRental(selector, from, to, tokenId);
+       } else if (selector == burn_From_selector) {
+           // Load the extension address from calldata.
+           address extension = address(
+               uint160(
+                    uint256(
+                       _loadValueFromCalldata(data, burn_From_selector_offset)
+                   )
+               )
+           );
+
+            _revertSelectorOnActiveRental(selector, from, to, tokenId);
+       } else if (selector == permit_selector) {
+           // Load the extension address from calldata.
+           address extension = address(
+               uint160(
+                    uint256(
+                       _loadValueFromCalldata(data, permit_selector_offset)
+                   )
+               )
+           );
+
+            _revertSelectorOnActiveRental(selector, from, to, tokenId);
+       } 
```

*Please note that there may be other flavours of the `permit` function that have different signatures.*


## Assessed type

Other
