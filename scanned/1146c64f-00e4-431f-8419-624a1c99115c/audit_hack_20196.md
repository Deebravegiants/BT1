# [M] 6.3.14OracleManager.setBeaconDatapossible front running attacks

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** River.1.sol#L27

**Description:** The system is designed in a way that depositors receive shares (lsETH) in return for their eth de-
posit. A share represents a fraction of the total eth balance of the system in a given time. Investors can claim their
staking profits by withdrawing once withdrawals are active in the system. Profits are being pulled fromELFeeRe-
cipientto theRivercontract when the oracle is callingOracleManager.setBeaconData.setBeaconDataupdates
BeaconValidatorBalanceSumwhich might be increased or decreased (as a result of slashing for instance).

Investors have the ability to time their position in two main ways:

- Investors might time their deposit just before profits are being distributed, thus harvesting profits made by
    others.
- Investors might time their withdrawal / selllsETHon secondary markets just before the loss is realized. By
    doing this, they will effectively avoid the loss, escaping the intended mechanism of socializing losses.

**Recommendation:** As for the first issue, we recommend considering replacing the accounting logic with a different
model that takes into account the timing of the deposit. In this case, as communicated with the team, oracles are
supposed to callOracleManager.setBeaconDataon a daily basis, which will limit the impact of such a strategy.
However, we do recommend the off-chain monitoring of oracles' activity to make sure that the impact of this issue
stays limited.

The second issue will have to be tackled once there is more certainty about the withdrawal process.

**Alluvial:** Resolved in SPEARBIT/13

**Spearbit:** It will solve the issue but will introduce further reliance on oracles, and will make it harder to track their
performance in general.

**Alluvial:** It indeed adds more opacity around operators but all the keys are inside the contract and anyone could
map the keys to the operators and track their performance. For now, we decided to move the operator rewards
outside of River and we will use an approach that is similar to what we were doing on-chain at first, but we will
work on adding more granularity to the rewards by taking into account how efficient their validators are. Adding
this on-chain would make everything a lot more complicated, the oracle reports would need to perform a huge ton
of extra work (we prefer having simple oracles that operators and integrators could easily run so we increase the
quorum as the protocol grows than requiring bigger hardware requirements and making it a pain to operate)

**Spearbit:** Acknowledged.
