# [M] M-06 | Circumvented Token Transfer Restrictions

## Summary
Severity: Medium
Contest weight: 0.1036
Dataset id: 22381
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERC20 tokens are non transferable when the contract is deployed. This is enforced with the transferable flag, preventing _transfer and _transferFromNFT to be executed when the from address is not the zero address, to allow token minting. The DN404 contract does not validate if the from address is the zero address in the transferFrom function. Therefore, users may call the function as follows: transferFrom(address(0), BOB, 0). The call will not revert, the transferable condition is circumvented, and a Transfer event will be emitted. Although there is no impact on user's balance, this is an unexpected behavior which may trick off-chain services.

## Recommendation
Consider overriding the DN404 transferFrom function to add the zero address check on the from address.
