# [M] M-02 | Double NFT Minting Via AfterNFTTransfer Hook

## Summary
Severity: Medium
Contest weight: 0.1997
Dataset id: 21304
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Contracts that extend DN404 can implement the _afterNFTTransfer hook to be executed after any NFT token transfers, including minting and burning. An attacker can abuse any implementations that pass access to holders from within these hooks as there are situations when the _afterNFTTransfer function is called before the internal storage is committed, breaking CEI. Consider the following attack scenario in a system implementing the _afterNFTTransfe hook: An approver initiates a transfer to a user where direct transfers will be made. In the _afterNFTTransfer function the malicious attacker has an existing helper contract that directly transfers several ERC721 tokens to himself. Since this was done before the balanceOf equivalent was updated, after the initial execution is finalized, the malicious strategy will have a smaller ERC721 balance then the number of ERC721 it owns. As the attacker has less NFTs then they should by the ownedLength variable and because this ownedLength is used in determining how many NFT a user will have for their base token amount, the attacker can transfer any amount, even 0, to himself and the contract will mint him extra ERC721 tokens, the exact number that was sent by the helper contract. At this point, an attacker owns double the ERC721 tokens that he received, for half the amount of ERC20 base required to own that many.

## Recommendation
Completely move the _afterNFTTransfer into its own separate loop in all cases except the call from _transferFromNFT which is already singular. In the particular case of direct transfer, also move it after setting the ownedLength.
