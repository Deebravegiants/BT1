# [M] M-02 | Council Members Cannot Set Challenge Period

## Summary
Severity: Medium
Contest weight: 0.0795
Dataset id: 2294
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inside TruthMarketManagerV2, several functions are available to manage the market's configuration
that can be called by the oracle council, such as setYesNoTokenCap, setEndOfTrading,
setFirstChallengePeriod, and setSecondChallengePeriod.
While setYesNoTokenCap and setEndOfTrading are currently available in the OracleCouncilV2
contract, setFirstChallengePeriod and setSecondChallengePeriod are not implemented, preventing
council members from configuring those market settings.

## Recommendation
Implement setFirstChallengePeriod and setSecondChallengePeriod inside OracleCouncilV2.
