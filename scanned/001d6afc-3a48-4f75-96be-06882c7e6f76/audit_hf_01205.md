# [C] Completed listings can be re-entered

## Summary
Severity: Critical
Contest weight: 0.2243
Dataset id: 5302
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the protocol, when the listing is completed by being sold or cancelled, nothing is changed about the listing's state, and when re-entering the listing, as long as the contract has the NFT of the listing, the listing is considered valid, even if the NFT belongs to another listing. This is because of the weak check in _isListingValid(). Consider the following scenario:
1. Alice lists NFT A for sale.
2. Bob buys NFT A and continues to sell it in the protocol.
3. Alice calls cancelListing() to cancel her completed listing, and since the contract owns NFT A (which actually belongs to Bob), the listing is still considered valid, so in cancelListing() the NFT A is returned to Alice, not Bob. The attacker can exploit this to steal the NFTs of other users in the contract. This problem also affects all other ways of settling the auctions (buyItNow(), settleAuction()).

## Recommendation
It is recommended to set the listing's state when the listing is complete (sold or canceled) and check that state when entering the listing. A reconfiguration of the function _isListingValid() is required.
