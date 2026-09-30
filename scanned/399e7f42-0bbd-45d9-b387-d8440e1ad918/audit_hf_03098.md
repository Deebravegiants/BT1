# [H] Attacker can front-run mintWithVault with a replayed signature to steal option NFT.

## Summary
Severity: High
Contest weight: 0.4174
Dataset id: 17479
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An attacker can front-run a writer’s call to mintWithVault with another transaction replaying the signature and other parameters as-is. Unlike mintWithERC721, mintWithVault does not perform access control to check if the option is being indeed minted by the token owner or operator. When it calls _mintOptionWithVault, it approves the msg.sender i.e. attacker for the new option NFT being minted which gives the attacker the right to transfer that to itself and pocket any spread later when the option gets settled in the future.
The call to mintWithVault fails the assumption made in the callee _mintOptionWithVault accounts, approve the msg.sender to transfer the option NFT as it already had the right to transfer the underlying NFT“ because the msg.sender is never checked against token owner or operator in mintWithVault as is done in mintWithERC721. This allows an attacker to front-run a writer’s call to mintWithVault with another transaction replaying the signature and other parameters as-is.
The writer’s original mintWithVault will fail because an active entitlement already exists for that asset from the attacker’s transaction. The front-running attacker becomes the option holder and can pocket the spread when the option gets settled in future.
Exploit scenario:
1. Alice deposits a BAYC NFT, currently valued by the market at 100 ETH, into a Hook vault.
2. Alice or her trusted relayer executes a mintWithVault corresponding to (1) with an entitlement signature and a strike price of 120 ETH.
3. Mallory observes Alice’s mintWithVault transaction in the mempool and front-runs it with the same parameters which is successful but Alice’s fails because hasActiveEntitlement reverts given the already active entitlement from Mallory’s transaction.
4. Mallory transfers the option NFT to herself and becomes the holder. There is nothing Alice can do to force reclaim the option NFT from Mallory.
5. Bidding happens until the option expires and is settled for e.g. say 130 ETH. The spread of (130 - 120) = 10 ETH is sent to Mallory. Alice gets the strike price of 120 ETH. The highest bidder gets the BAYC NFT for 130 ETH.
6. Alice effectively suffers a loss of at least 10 ETH (the spread) which could have been hers if the option NFT had been minted to her as she expected. She could have pocketed the spread of 10 ETH or sold the option NFT earlier off-protocol for perhaps an even higher price.
The NFT owner and option writer suffers a loss of value at least equivalent to the spread which was captured by the front-running attacker.

## Recommendation
Enforce access control in mintWithVault to ensure that the caller is the token owner (i.e. writer) or operator (as is done in mintWithERC721).
Add erc721-style approve and getApproved. Require that msg.sender is beneficial owner or approved for imposeEntitlement, mintWithVault, mintWithEntitledVault
https://github.com/hookart/protocol/pull/46
Rajeev: This adds a new access control approval mechanism on top of ERC721 which is confusing. Seems to work but wonder if there are interaction risks from inconsistent ERC721 owner/spender/operator roles.
WatchPug: We can not use ERC721's approval mechanism directly as the NFT is now held by the vault and using ERC721's approval means the operator can transfer the NFT out.
Maybe consider changing the name to `getApprovedOperator`, `_approveOperator` to avoid misunderstanding?
I've updated the naming in this PR. The goal here is to ensure that approvals CANNOT be set on tokens in the vault as an invariant.
https://github.com/hookart/protocol/pull/71
Verified fix.
