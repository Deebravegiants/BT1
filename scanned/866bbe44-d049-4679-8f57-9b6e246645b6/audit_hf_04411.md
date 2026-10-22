# [C] C-01 | GLV Arbitraged With pnlToPoolFactor

## Summary
Severity: Critical
Contest weight: 0.3476
Dataset id: 21887
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upon deposits to GLV the GM tokens in the vault are valued using the MAX_PNL_FACTOR_FOR_DEPOSITS,
and on withdrawals the GM tokens in the vault are valued using the
MAX_PNL_FACTOR_FOR_WITHDRAWALS.
The MAX_PNL_FACTOR_FOR_DEPOSITS will value GM tokens at a lower value than the
MAX_PNL_FACTOR_FOR_WITHDRAWALS as the trader’s PnL is capped using a higher percentage, resulting
in more trader proﬁts being allowed using the deposit pnlToPoolFactor measurement.
In the existing GMX V2 system this is not exploitable since withdrawals are not allowed if the market is over
the MAX_PNL_FACTOR_FOR_WITHDRAWALS ratio. However in GLV there is no constraint on withdrawing a
different GM market using your GLV tokens and beneﬁting from this arbitrage in total GLV value between
deposits and withdrawals.
For example:
• GLV has GM A and GM B
• The GM A MAX_PNL_FACTOR_FOR_WITHDRAWALS is 40% and MAX_PNL_FACTOR_FOR_DEPOSITS is 60%
• GM A has +$500,000 of pending trader PnL and the pnlToPoolFactor is currently 50%
• User A deposits GM B to the GLV, the GLV is valued using MAX_PNL_FACTOR_FOR_DEPOSITS which allows
for the full trader pnl of $500,000
• User A then withdraws GM B from the GLV, the GLV is valued using
MAX_PNL_FACTOR_FOR_WITHDRAWALS which allows for only $400,000 of trader pnl, which values the GM
A tokens higher.
As a result User A receives more GM B out of the withdrawal than they had initially deposited because of the
arbitrage between the deposit factor and withdrawal factor.

## Recommendation
Consider valuing all GM tokens in the GLV using the MAX_PNL_FACTOR_FOR_DEPOSITS even on
withdrawals. This way the value of the GM tokens is minimized when the pnlToPoolFactor is currently above
the withdrawal factor. This would inaccurately account for the value out of the GM tokens a user would
receive if they withdrew those tokens, however those tokens would not be withdrawable if they are above this
factor anyways.
Alternatively, consider disallowing all GLV withdrawals when any one of the market tokens is above it’s
MAX_PNL_FACTOR_FOR_WITHDRAWALS.
