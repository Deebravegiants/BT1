The user is asking to identify similar vulnerabilities to the described `Permissionless voting through Voter::carryVoteForward()` in other projects within the `AllProjects` repository. The core of the vulnerability is a lack of access control on a function that can manipulate voting outcomes.

I found a similar vulnerability in the DeXe Protocol project, specifically related to the `recalculateNftPowers` function in `ERC721RawPower.sol` and `ERC721EquivalentPower.sol`.  This function lacks access control, allowing any unprivileged user to manipulate the `totalRawPower` value, which is used in calculating the quorum for governance proposals. 

### Title
Permissionless manipulation of governance quorum - ([Project: DeXe Protocol] [File: contracts/gov/ERC721/powers/ERC721RawPower.sol])

### Summary
The `recalculateNftPowers` function in `ERC721RawPower.sol` and `ERC721EquivalentPower.sol` lacks access control, allowing any external address to reduce the `totalRawPower` used in quorum calculations. This can lead to proposals passing quorum that would otherwise fail, effectively manipulating governance voting results.

### Finding Description
The `GovPoolVote._quorumReached` function calculates the quorum using `IGovUserKeeper(userKeeperAddress).getTotalPower()`, which is a live value.  For NFT-based voting, `getTotalPower()` adds `IERC721Power(nft).totalPower()`, which for `ERC721RawPower` is the mutable `totalRawPower`.  The `totalRawPower` is reduced by the `recalculateNftPowers` function in `ERC721RawPower.sol` (and `ERC721EquivalentPower.sol`), which has no owner check or access control.  This function strictly lowers the aggregate `totalRawPower` because it updates lazily maintained power values with potentially decayed live values. 

### Impact Explanation
An attacker can call `recalculateNftPowers` for NFTs whose power has decayed, thereby reducing the `totalRawPower` and consequently the quorum denominator.  This makes it easier for proposals to reach quorum and become executable, even if the actual votes cast would not have met the original quorum threshold.  This directly leads to the manipulation of governance voting results, which is classified as a Critical impact in the DeXe Protocol bug bounty program. 

### Likelihood Explanation
The likelihood is high because the `recalculateNftPowers` function is `external` and lacks any access control, meaning any unprivileged user can call it at any time.  The attack only requires identifying NFTs with decayed power, which is a common characteristic in time-based voting power systems. 

### Recommendation
Implement access control on the `recalculateNftPowers` function to ensure that only authorized entities (e.g., the contract owner or a designated governance module) can trigger the recalculation of NFT powers. This would prevent arbitrary users from manipulating the quorum denominator.

### Proof of Concept
1. A governance proposal is created and accumulates `votesFor` that are close to, but do not yet meet, the quorum threshold based on the current `totalRawPower`. 
2. An unprivileged attacker identifies a set of NFTs whose `currentRawPower` has decayed significantly since their `totalRawPower` was last updated. 
3. The attacker calls `ERC721RawPower.recalculateNftPowers()` (or `ERC721EquivalentPower.recalculateNftPowers()`) with the `tokenIds` of the identified decayed NFTs. 
4. This call reduces the `totalRawPower` maintained by the `ERC721RawPower` contract. 
5. Subsequently, any `vote` or `cancelVote` operation on the proposal will re-evaluate the quorum via `_updateGlobalState` -> `_quorumReached`. 
6. Due to the reduced `totalRawPower` (the denominator), the `PERCENTAGE_100.ratio(core.votesFor, totalPower)` calculation now meets or exceeds the `core.settings.quorum`. 
7. The proposal becomes executable, even though it did not genuinely meet the quorum under the original conditions. 

## Notes
The external report describes a vulnerability in `Voter::carryVoteForward()` where any user can manipulate votes for an NFT without the owner's authorization.  The analog found in DeXe Protocol's `ERC721RawPower.sol` and `ERC721EquivalentPower.sol` is similar in that a public function (`recalculateNftPowers`) allows an unprivileged user to manipulate a critical governance parameter (`totalRawPower`), which indirectly affects voting outcomes by altering the quorum calculation.  Both vulnerabilities stem from a lack of access control on a function that can influence voting mechanics. 

Wiki pages you might want to explore:
- [Overview: AllProjects Audit Corpus (AuditingProject/AllProjects)](/wiki/AuditingProject/AllProjects#1)

View this search on DeepWiki: https://deepwiki.com/search/-analog-scan-prompt-external-r_647a5b60-40eb-4331-a1b4-99c769873361
