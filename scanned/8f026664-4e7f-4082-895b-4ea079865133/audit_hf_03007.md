# [H] `_transferFrom`

## Summary
Severity: High
Contest weight: 0.2353
Dataset id: 16790
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an accounting flaw in the delegation logic of an ERC721‑based voting token. The contract treats each token as an active vote for its holder even when the holder has not explicitly delegated that token, contrary to the intended OpenZeppelin ERC721Votes design where votes are only counted after delegation. Because the internal _transferFrom routine calls the helper _moveDelegateVotes with the raw sender and recipient addresses, the system moves voting power from the token owner rather than from the owner’s current delegate. As a result, a token holder can delegate to a fresh address, transfer the token to another address they control, and then delegate again, causing the contract to credit an additional vote each time the token changes hands. By repeating the create‑address, delegate, transfer loop, an attacker can accumulate an arbitrarily large amount of voting power without acquiring additional tokens, effectively achieving infinite voting influence. This exploit can be triggered whenever a holder is able to create new Ethereum addresses (which is trivially cheap) and perform token transfers, i.e., under normal usage conditions of the governance token. The affected parties include all token holders, the governance process of the protocol, and any downstream decisions that rely on a fair vote count. The issue was discovered during a security audit that compared the implementation against the OpenZeppelin reference and noticed that votes were being counted without a delegate, and that the delegation mapping was not consulted when moving votes on transfer. The flaw is subtle because the contract still records token balances correctly, so typical balance‑related checks pass, and the vote count appears to increase in a linear fashion without obvious arithmetic errors, making it hard to detect without explicit vote‑tracking tests. To remediate, the vote‑movement logic must reference the delegations of the sender and the receiver, i.e., it should transfer voting power from delegation[_from] to delegation[_to] and only count votes for addresses that have been delegated to. Additionally, the contract should enforce that tokens do not contribute to voting power until a delegation transaction is executed, matching the intended design of ERC721Votes. By fixing the delegation accounting and ensuring votes are only minted upon explicit delegation, the protocol restores its intended one‑vote‑per‑token governance model and eliminates the possibility of unlimited vote inflation.

## Recommendation
Looking at [OpenZeppelin’s ERC721Votes](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/6a8d977d2248cf1c115497fccfd7a2da3f86a58f/contracts/token/ERC721/extensions/draft-ERC721Votes.sol#L13) which I believe the team took reference from, it states:
    
    * Tokens do not count as votes until they are delegated, because votes must be tracked which incurs an additional cost
    * on every transfer. Token holders can either delegate to a trusted representative who will decide how to make use of
    * the votes in governance decisions, or they can delegate to themselves to be their own representative.

The current implementation does not follow this, and tokens count as votes without being delegated. To fix this issue, votes should only be counted when delegated.

  * I believe the issue is here on this [line](https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/lib/token/ERC721Votes.sol#L268)

    // Transfer 1 vote from the sender to the recipient
            _moveDelegateVotes(_from, _to, 1);

Where it should move from the delegate of `_from` to the delegate of `_to`. Suggested FIx:
    
     _moveDelegateVotes(delegation[_from], delegation[_to], 1);

Would agree w/ High risk.

The Warden has shown how, due to an incorrect handling of delegation, a Token Holder can delegate their voting power without losing it, allowing for an exploit that allows them to reach infinite voting power.
 
I believe that some of the problems with Delegation shown via this contest can be traced down to this quote from the [OZ Documentation](https://docs.openzeppelin.com/contracts/4.x/api/token/erc721#ERC721Votes) `Tokens do not count as votes until they are delegated, because votes must be tracked which incurs an additional cost on every transfer. Token holders can either delegate to a trusted representative who will decide how to make use of the votes in governance decisions, or they can delegate to themselves to be their own representative.`
 
Remediation of this specific issue can be done by following the warden advice, and using the Test Case to verify the exploit has been patched, additionally, further thinking into how delegation should behave will be necessary to ensure the system is patched to safety

In contrast to [issue 469](https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/469) (Unsafe Underflow) and [issue 413](https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/413) (Self Delegation for doubling of votes), this report is showing how, due to an incorrect accounting, a user can repeatedly transfer and delegate to achieve infinite voting power.
 
While the outcome of all 3 is increased voting power, I believe the uniqueness of the attack is in exploiting a different aspect of the code.
 
Remediation should account for all 3 exploits, and I believe, because of the uniqueness of the attack, that this is a distinct report vs the previously mentioned.
