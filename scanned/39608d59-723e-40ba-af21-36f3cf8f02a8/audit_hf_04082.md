# [M] FIVF-1 | Liquidation Needs To Match Pending Output Token

## Summary
Severity: Medium
Contest weight: 0.1281
Dataset id: 20535
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The expectedConversionToken validation is meant to ensure that the values of two different tokens
aren't added and subtracted in the _accountInfoToPendingAmountWeiMap and
_vaultToPendingAmountWeiMap mappings.
Due to this check, liquidations will fail if the outputToken does not match the outputToken on a
pending deposit/withdrawal. Forcing liquidations to use a speciﬁc outputToken can lead to less
long/short token being withdrawn on redemption by experiencing negative price impact when
swapping to that particular outputToken.
Furthermore, because the Oracle assumes liquidations are typically performed from long token to
short token, a user could further exacerbate the price impact mispricing by forcing a liquidation from
short to long token instead.

## Recommendation
Reconsider if the expectedConversionToken check is even necessary. The _amountDeltaWei.value is
always in GM, so subtracting two different token values should not occur. However, this would
require a change to the _accountInfoToOutputTokenMap as an account could be experiencing two
different conversion tokens.
