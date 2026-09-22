# [M] 5.2.13claimToTreasury(COMP)steals users' COMP rewards

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** compound/MorphoGovernance.sol#L

**Description:** TheclaimToTreasuryfunction can send a market's underlying tokens that have been accumulated
in the contract to the treasury. This is intended to be used for the reserve amounts that accumulate in the contract
from P2P matches. However, Compound also pays out rewards in COMP and COMP is a valid Compound market.
Sending the COMP reserves will also send the COMP rewards. This is especially bad as anyone can claim COMP
rewards on the behalf of Morpho at any time and the rewards will be sent to the contract. An attacker could even
frontrun aclaimToTreasury(cCOMP)call with aComptroller.claimComp(morpho, [cComp])call to sabotage the
reward system. Users won't be able to claim their rewards.

**Recommendation:** If Morpho wants to support the COMP market, consider separating the COMP reserve from
the COMP rewards.

**Morpho:** Given the changes to do and the small likelihood to set a reserve factor for the COMP asset and the
awareness on our side about this, we decided not to implement it.

**Spearbit:** Acknowledged.
