# [M] MKTU-2 | minFundingFactorPerSecond != 0 Undesired behaviors

## Summary
Severity: Medium
Contest weight: 0.1584
Dataset id: 19214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The funding factor per second returned from the getNextFundingFactorPerSecond function may be
unable to cross from negative to positive or from positive to negative in the event that the
minFundingFactorPerSecond is set > 0 and orders are executed often.
Original savedFundingFactorPerSecond = 10
minFundingFactorPerSecond = 10
nextSavedFundingFactorPerSecond = 7
Bounded nextSavedFundingFactorPerSecond = 10
The nextSavedFundingFactorPerSecond cannot ﬂip signs and continue to make progress to reach
the funding factor it ought to be on the other side unless it can make a large enough jump to cross
the gap from [0, minFundingFactorPerSecond], which may be unlikely if orders are consistently
updating the secondsSinceFundingUpdated.
Additionally, if the gap from [0, minFundingFactorPerSecond] is crossed successfully, the resulting
nextSavedFundingFactorPerSecond will be increased in magnitude to the
minFundingFactorPerSecond, resulting as -minFundingFactorPerSecond. This jump will go above the
conﬁgured fundingIncreaseFactorPerSecond rate and may cause unexpected results.

## Recommendation
Be wary when conﬁguring the minFundingFactorPerSecond to be != 0, if the minFundingFactor is
ever != 0 it should have a minimal magnitude to limit these behaviors.
