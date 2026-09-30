# [M] The onERC721Received() Is Not Implemented Correctly

## Summary
Severity: Medium
Contest weight: 0.1999
Dataset id: 15777
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PositionManager.onERC721Received() function intends to accept liquidity positions sent only by the admin to the PositionManager contract. It performs some validations regarding the liquidity position type that is being transferred and records the pair so other liquidity positions in the same pair are not accepted. An attacker can exploit the safeTransferFrom() function by front-running the admin’s transaction and invoking the PositionManager.onERC721Received() function with crafted arguments. Specifically, the attacker can set the from parameter to the admin’s address to bypass the require(hasRole(DEFAULT_ADMIN_ROLE, from), "...") check, which validates the sender’s role. By specifying a tokenId corresponding to the same pair the admin is attempting to transfer—one that the admin does not control—the attacker causes the admin’s safeTransferFrom() call to revert. This effectively prevents the admin from transferring a liquidity position for the targeted pair, creating a denial-of-service scenario for this specific operation. The admin, and indeed anyone, can still send liquidity positions to the PositionManager using the transferFrom() function instead of safeTransferFrom(). However, doing so will result in the _uniV3NftByToken0Token1 and _uniV3NftIds mappings not being updated, rendering them inaccurate and effectively useless.

## Recommendation
To limit liquidity positions the PositionManager interacts with, remove the onERC721Received() override and implement an admin-only deposit function. This function can call safeTransferFrom(), perform necessary checks, and record deposited tokenIds for verification in other functions. Currently, functions like addLiquidity(), collectFees(), and collectFeesOnly() accept tokenIds transferred by anyone, which can be secured by using this deposit mechanism.
