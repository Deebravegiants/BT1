# [H] H-06 | Missing Liquidation Callback Case

## Summary
Severity: High
Contest weight: 0.3250
Dataset id: 21946
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During a liquidation, the receiver variable is set to the account address, which in this case is the
GmxUtils contract. Since the GmxUtils contract doesn’t set a savedCallbackContract (which is used
as the callback contract for liquidations), the callback address will default to the zero address.
As a result, the callback will not be triggered, meaning the afterOrderExecution function in the
GmxUtils contract, which is meant to send the liquidated funds to the perpetualVault contract won’t
be triggered. This causes the funds sent to the GmxUtils contract to become stuck with no way to
retrieve them.
Additionally, interacting with the protocol after said liquidation can lead to DoS's and incorrect fund
and share allocation. This is in part because liquidations will close the position which results in
withdraw attempts failing when the settle order executes.
After the failed execution Gamma will retry the settle over and over failing each time. Deposits also
present a special case where the deposit may underﬂow _totalAmount(marketPrices) could be less
than amount: totalAmountBefore = _totalAmount(marketPrices) - amount;

## Proof of Concept
https://github.com/GuardianAudits/gamma-gmx-2/blob/POC_LIQ_UNHANDLED/test/guardian/pocs/LiquidationsUnhandled.sol

## Recommendation
The GmxUtils contract should set the savedCallbackContract so the afterOrderExecution function in
the GmxUtils contract is called during ADLs or liquidations.
Additionally, consider handling the liquidation case where after funds are sent back to the
perpetualVault there are speciﬁc actions taken to get the protocol to a state where DOS's will not
occur. This includes updating the state so that Gamma has the position as closed. It also includes
preparing the state for any upcoming or incoming deposits/withdrawals.
Set positionIsClosed to true and curPositionKey to bytes32(0) in afterOrderExecution(). Also,
conﬁgure the callback via setSavedCallback(), and expect the call for liquidations to originate from
GMX’s LiquidationHandler contract in validCallback().
