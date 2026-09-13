# [M] 5.2.2 Lack of replay protection formintAllowListandmintSigned

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** SeaDrop.sol#L227, SeaDrop.sol#L
**Description:** In the case of mintSigned (minting via signatures) and mintAllowList (minting via
merkle proofs) there are no checks that prevent re-using the same signature or Merkle proof multiple
times. This is indirectly enforced by the _checkMintQuantity function that checks the mint statistics
using IERC721SeaDrop(nftContract).getMintStats(minter) and reverting if the quantity exceeds
maxMintsPerWallet.
Replays can happen if a wallet does not claim all ofmaxMintsPerWalletin one transaction. For example, assume
thatmaxMintsPerWalletis set to 2. A user can callmintSignedwith a valid signature andquantity = 1twice.
Typically, contracts try to avoid any forms of signature replays, i.e., a signature can only be used once. This simpli-
fies the security properties. In the current implementation of theERC721Seadropcontract, we couldn't see a way to
exploit replay protection to mint beyond what could be minted in a single initial transaction with the maximum value
ofquantitysupplied. However, this relies on the contract correctly implementingIERC721SeaDrop.getMintStats.
**Recommendation:** We recommend implementing replay protection for both cases. Here are some ideas to do
this:

1. Consider also including thetokenIdfor the signature and passing that along inmintSeaDropcall. This way,
    even if the signature is replayed, minting the sametokenIdshould not be possible--most ERC-721 libraries
    prevent this. However, some care should be made to check the following case: mint a fixed token id using
    the signature, then burn the token id, and resurrecting the same token id by replaying the signature.


2. Consider storing the digest and if a digest is used once, then it shouldn't be able to use again.
3. Do not use signature as a way to check if something was consumed. They are malleable.
**OpenSea:** We discussed replay-protection here, and decided it was a more or less acceptable risk for the following
reasons:
1. Allow-lists, which also_checkMintQuantityare likewise not redeemed, so Merkle proofs can be re-used in
the same way, up to the maximum mint quantity
2. Also like allow-lists, the supplied MintParams specify astartTimeandendTime; a signature can supply a
short window (minutes) for consumption before a new signature needs to be generated
3. A broken_checkMintQuantityor unreasonably largemaxTokensMintablequantity is likely (though not al-
ways) exploitable in the first time a signature (or Merkle proof) is used
However! Riffing off of thetokenIdsuggestion (We don't think it's possible to know exactly which starting token ID
a given tx will mint), since we're already checkingminterNumMinted; we could include that as part of the signature
to prevent re-use.
**Spearbit:** 2. A malicious user can always get around thestartTimeandendTimelimits, using some automation.
3. We think that most ERC-721 contracts would assume that Opensea would handle the signature verification
and replay protection--the burden of the sale mechanism should be on the Seadrop contract. Also, because
this requires the ERC-721 contract to keep track of the number of the number of tokens minted by an address.
ERC721A tracks this, but neither Solmate, nor Openzeppelin does this currently. We'd expect some user errors
because of this problem.
