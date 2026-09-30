# [M] M-05 | Initiators Avoid A Portion Of Funding

## Summary
Severity: Medium
Contest weight: 0.1920
Dataset id: 142
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When initiating a position the user’s exposure is computed accounting for the current funding rate accrued to the latest block.timestamp. However upon initiation users can affect the funding directly after the initiation is complete in the following time range [initiationLastUpdateTimestamp, initiationBlockTimestamp] as long as a subsequent action is performed with another price before or near the initiationLastUpdateTimestamp. This way users who initiate do not have to incur the cost of the existing funding rate over the range [initiationLastUpdateTimestamp, initiationBlockTimestamp], meanwhile their positions are affecting the skew and thus should incur the full funding cost. These positions will incur the difference in the funding rate that they cause, but not the base funding rate that was pre-existing before they initiated their position. If positions are not held accountable for the total funding rate in the range [initiateLatestPriceTimestamp, initiateBlockTimestamp], then they can force other long positions to pay for increased funding, by way of increasing the long exposure, while not paying for it themselves. This may allow for extractable value for a USDN depositor or cause other positions to be liquidatable by this manipulation.

## Proof of Concept
https://gist.github.com/GuardianAudits/96d7fa8499458e1d11d94e96baea0b54

## Recommendation
Consider only using the long exposure without syncing the funding to the latest timestamp, e.g. UsdnProtocolCoreLibrary.longTradingExpoWithFunding(s, lastPrice, uint128(s._lastUpdateTimestamp)). Or simply, s._totalExpo - s._longBalance.
