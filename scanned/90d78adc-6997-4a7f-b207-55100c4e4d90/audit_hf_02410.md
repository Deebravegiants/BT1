# [M] An attacker can create a short put option order on an NFT that does not support ERC721

## Summary
Severity: Medium
Contest weight: 0.1521
Dataset id: 12971
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An attacker can create a short put option on cryptopunk. When the user fulfills the order, the baseAsset will be transferred to the contract.

However, since cryptopunk does not support ERC721, the user cannot exercise the option because the safeTransferFrom function call fails. Attacker can get premium and get back baseAsset after option expires.

## Recommendation
Consider adding a whitelist to nfts in the order, or consider supporting exercising on cryptopunk.

Putty uses solmate’s `ERC721.safeTransferFrom` which requires that the NFT contract implements `onERC721Received`. For the case of OG NFTs like punks and rocks, this will fail, <https://github.com/Rari-Capital/solmate/blob/main/src/tokens/ERC721.sol#L120>
The user does not need to send cryptopunk to the contract when fulfilling the short put option order, but the user will pay a premium to the order creator. Later, when the user wants to exercise the option, since the cryptopunk does not support safetransferfrom, the user cannot exercise the option.

Sorry, I did not consider this path. You are correct to say that a maker can create a short put option order with cryptopunks as a token and the holder of the long put option will not be able to exercise since cryptopunks cannot be transferred with `safeTransferFrom`. From that perspective, this is a valid issue. Thank you for bringing it up. I will defer to the judge for the final decision.

We dont intend to support cryptopunks or cryptokitties. If users wish to use these tokens then they can get wrapped versions (ex: wrapped cryptopunks).
I thought cryptokitties are ERC721? I think they were the ones who popularized the standard actually :p Probably meant etherrocks.

In general, non-compliant ERC-721 NFTs can be supported through wrappers, though some users might be unaware… Downgrading to med severity, similar to [this issue from another contest](https://github.com/code-423n4/2022-02-foundation-findings/issues/74).

**hyh (warden) reviewed mitigation:**
Similar to [M-01](https://github.com/code-423n4/2022-06-putty-findings/issues/50), [M-02](https://github.com/code-423n4/2022-06-putty-findings/issues/227).
