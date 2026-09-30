# [M] M-34 | Old Vault Validations Swing USDN Price

## Summary
Severity: Medium
Contest weight: 0.2826
Dataset id: 200
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
https://github.com/GuardianAudits/usdn-1/blob/7462fc4d1b886129a4091dfc91ff5304d1d3a970/src/UsdnProtocol/libraries/UsdnProtocolVaultLibrary.sol#L576
The behavior of the deposit ﬂow is such that a user’s shares are not minted and their deposited amount is not added to the vault balance until validation time. This however causes several issues related to funding and the price of USDN. The minting of shares is an activity that changes the price of shares when the ratio used to mint is stale.
For example:
• validationPrice is $80 from 30 minutes ago (initiation price is the same)
• Current market price is $100
• Vault balance is 100 wstEth at the current market price
• Vault balance is 120 wstEth at the validationPrice
• Deposit is for 10 wstEth
• There are 10,000 total vault shares
• Divisor is 1
• USDN price is 100 wstEth * $100 / 10,000 shares = $1
• If the deposit validation were to occur at the current market price the user would receive 10 * 10,000 / 100 = 1,000 shares
• USDN price at the current market price would be: 110 wstEth * $100 / 11,000 shares = $1
• However the deposit validation takes place at the validation price, which is the most recent price after the initiation + 24 seconds.
• Therefore the user receives shares: 10 * 10,000 / 80 = 1,250 shares
• USDN price at the current market price is now: 110 wstEth * $100 / 11,250 shares = $0.9777
Thus the price of USDN experiences a stepwise change which can be non-trivial, a similar issue exists with withdrawals as well. Furthermore, there are other less obvious issues regarding funding with the current deposit accounting. Firstly, depositors are forced to be held accountable for the funding that occurs in the timeframe [initiationTimestamp, validationTimestamp] even though their deposited amounts are not added to the vaultBalance until validationTimestamp and thus have not affected the skew for this period.
Secondly, depositors are forced to be held accountable for the difference in funding which occurs over the [initiationLastPriceTimestamp, initiationTimestamp] period versus the predicted amount of funding which would occur in that timeframe which is computed here:
https://github.com/GuardianAudits/usdn-1/blob/7462fc4d1b886129a4091dfc91ff5304d1d3a970/src/UsdnProtocol/libraries/UsdnProtocolVaultLibrary.sol#L576.

## Recommendation
Use the same approach as for the open position actions for the deposit actions. Mint the shares up front and let the deposited amount directly be added to the vaultBalance, but do not give the shares to the user yet. Upon validation issue a correction to the shares received by the user based upon the price difference between initiation and validation.
This will result in a stepwise jump in share price similar to the one experienced when using the _validateOpenPositionUpdateBalances function during the open position ﬂow, however this stepwise jump will be far more insigniﬁcant than the one experienced currently due to old deposit validations.
The same approach should be taken for vault withdrawals, similar to the closing of positions. Another solution would be to simply require all prices to be much more recent than the current conﬁgurations which would reduce the potential worse case magnitude of the stepwise jump described in this ﬁnding.
