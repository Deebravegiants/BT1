# [C] The TUSD market case

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Up until recently, the TUSD token had two different entry points: the current implementation, which lives behind a proxy deployed at , and a legacy contract that forwarded calls to the current contract, writing its storage when the `transfer`, `transferFrom`, `increaseApproval`, `decreaseApproval`, and `approve` functions were called. This introduced an undesired behavior: anyone would be able to call the `sweepToken` function of the CTUSD contract sending as the parameter the legacy contract address, effectively moving all the underlying from the CTUSD contract to the Timelock.

The issue lies in the fact that the `totalCash`, in the numerator of the `exchangeRate` formula described above, can be moved to 0 by calling the `sweepToken` function, and given the amount of underlying that is not being used for borrows in the TUSD market (roughly 50% of the TVL), the exchange rate could be moved down by around 50%.

This means that after calling the sweep function, the following would happen:

* The exchange rate, which tracks the borrow rate, and should always be an increasing function, will go down by \~50%
* Any supplier that adds TUSD to the market will receive \~2x the cTUSD amount they should. (A malicious supplier could discover this bug, call the sweep function, and then immediately add liquidity)
* Any supplier that provided liquidity to the market _before_ the sweep and then redeems their liquidity after the sweep will receive roughly 50% less of the underlying asset than they should. This would only be possible if suppliers added liquidity at an inflated exchange rate after the sweep. Until the sweep is reversed, they will not be able to redeem any amount
* Even if the Timelock moves the funds back to the CTUSD contract, the relationship between the cTUSD supply and underlying assets can be permanently changed due to overminted cTUSD tokens. The interest rates would then remain negative, ultimately putting the market in a loss state for previous suppliers. The degree of the negative rates would depend on the amount of cTUSD tokens minted after the sweep: The more inflated cTUSD tokens minted after the sweep, the more negative the interest rate would be

The exact amounts can be found in this [spreadsheet](https://docs.google.com/spreadsheets/d/1%5FyHiLFN1mTxFi7np-8ZNmuHb3z8PpHMFn4IdKer1j98/edit#gid=409366094).

On February 23rd 2022, the TUSD team disallowed forwarded calls from the legacy contract to the current contract by rejecting them from the latter, ultimately fixing the issue.


None.


None.
