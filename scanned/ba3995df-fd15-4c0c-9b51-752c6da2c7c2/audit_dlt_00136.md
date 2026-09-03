# [H] GovernorVotesQuorumFraction updates to quorum may affect past defeated proposals

## Summary
Severity: High
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
CVE: CVE-2022-31198
Published: 2022-07-28
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-xrc4-737v-9q75
Type: github-advisory

## Details
### Impact

This issue concerns instances of Governor that use the module `GovernorVotesQuorumFraction`, a mechanism that determines quorum requirements as a percentage of the voting token's total supply. In affected instances, when a proposal is passed to lower the quorum requirement, past proposals may become executable if they had been defeated only due to lack of quorum, and the number of votes it received meets the new quorum requirement.

Analysis of instances on chain found only one proposal that met this condition, and we are actively monitoring for new occurrences of this particular issue.

### Patches

This issue has been patched in v4.7.2.

### Workarounds

Avoid lowering quorum requirements if a past proposal was defeated for lack of quorum.

### References

https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3561

### For more information

If you have any questions or comments about this advisory, or need assistance deploying the fix, email us at [security@openzeppelin.com](mailto:security@openzeppelin.com).
