# [M] Candy Machine Set Collection During Mint Missing Check

## Summary
Severity: Medium
Advisory: GHSA-9v25-r5q2-2p6w
Ecosystem: crates.io
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-9v25-r5q2-2p6w
Type: github-advisory

## Affected
- crates.io: `mpl-candy-machine` — affected >=4.5.0 <4.5.1

## Details
A problem with Candy Machine V2 allow minting NFTs to an arbitrary collection due to a missing check.

Here is a description of the exploit:
Details:
Here is the tx/ix to exploit:
Transaction:
Ix 1: candy_machine v2, mint_nft, passing in empty metadata -1
Ix 2: custom handler, 0
		cpi A --> token_metadata create_metadata_account, creates NFT
		cpi B --> candy_machine v2, set_collection_during_mint
Ix 1 passes our first check for empty metadata, but eventually will hit a bot tax and return Ok.  We do have a CPI check in this function but even if we hit that or moved it to the top, it returns Ok as a bot tax and still enables the issue.
Ix 2, cpi A is Ok and mints an arbitrary NFT.
Ix 2, cpi B checks the previous instruction using index_relative_to_current-1.  This turns out to be Ix 1 which was Ok, so then your newly minted arbitrary NFT is successfully added to the collection.
Conclusion:
Candy machine could be out of NFTs and it still works.  If the CM is closed, (we think?) it doesn't get to the check.
The fix needs to be in set_collection_during_mint that current program ID id candy_machine_v2.  It checks previous program ID but doesn't check current.

NOTE: THIS DOES NOT AFFECT Cmv3

## References
- https://github.com/metaplex-foundation/metaplex-program-library/security/advisories/GHSA-9v25-r5q2-2p6w
- https://github.com/metaplex-foundation/metaplex-program-library/commit/e6b3aff603ac06236bf77c2ec21ead93c6836dce
- https://github.com/metaplex-foundation/metaplex-program-library
