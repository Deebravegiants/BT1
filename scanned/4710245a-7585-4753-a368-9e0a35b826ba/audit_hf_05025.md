# [M] Uniswap governance increase of protocol fees

## Summary
Severity: Medium
Contest weight: 0.2740
Dataset id: 23025
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Aloe calculates IV based on feeGrowthGlobal (fgg which is the fees per liquidity unit
collected over the FEE_GROWTH_AVG_WINDOW) and gamma (percentage of fees received
by LPs from the trading volume, which is the trading fee percentage less protocol
fee percentage), more specifically IV is in direct proportion to sqrt(fgg) and to
sqrt(gamma). If Uniswap Governance changes the protocol fees setting, fgg remains
the same, but the gamma value instantly drops, meaning calculated new IV will also
instantly drop (by sqrt(gamma_new / gamma_old)). This will cause a steady decline
of IV over the next FEE_GROWTH_AVG_WINDOW (72 hours) regardless of market
conditions, meaning the IV will be artificially deflated. Since the protocol asseses
borrowers health based on IV, this deflated IV will lead to more risky borrower
positions becoming acceptable with increased risk of bad debt liquidations, and
bad debt will cause lenders to lose funds since they won't be able to withdraw all
funds due to bad debt. This breaks protocol risk expectations.
The FeeGrowthGlobals stored in the protocol are just direct values from the uniswap
pool, meaning this is just raw fees collected per liquidity unit:
/VolatilityOracle.sol#L149-L156
If/when uniswap governance changes protocol fees, anyone can call
VolatilityOracle.prepare to reflect these changes in the internal cache:
/VolatilityOracle.sol#L39-L46
Once prepare is called, gamma values instantly change to a new value. And gamma
-aloe-update/blob/main/aloe-ii/core/src/libraries/Volatility.sol#L61-L85
This causes an instant change in IV value as well. So the root cause is that only
collected fees (fgg) are stored during VolatilityOralce updates instead of volume
amount derived from it (fgg * gamma).
Internal pre-conditions
The only condition is for any user to call VolatilityOracle.prepare to reflect
uniswap protocol fees in the internal cache. Since this is permissionless function,
it's very easy for anyone to call it.
External pre-conditions
Uniswap governance increases protocol fees.
Attack Path
Once pre-conditions are met, nothing is needed to do - IV will always drop
regardless of any other actions.
New (target) IV instantly drops. Due to per-second and per-update IV change
limitations, the actual IV used in collateral calculations will predictably go down
slowly. So while this limits the impact, it still causes IV to decline below expected
levels temporarily. In the worst case, the protocol fees are set from 0 to 1/4 (max
value allowed in uniswap). This will cause the target IV to decrease by ~14%. The
actual IV decrease will be limited by IV change safeguards and will depend on
circumstances. Since per-update (every 4 hours) IV only actually changes by 1% of
difference between target and current volatility, this means that over the 72 hours
window the IV will decrease by at most 2.52%. This might be more impactful if
actual volatility increases significantly during the same time, but the issue
described here will not allow IV to increase and will keep it decreasing.
The incorrect (deflated) IV will cause more risky borrower positions to be healthy
which increases risk of bad debt, which is a loss for the lenders and possible bank
run, since the last lenders to withdraw will be unable to do so due to bad debt.

## Proof of Concept
Not needed (instant change/jump of target IV after uniswap protocol fee change is
obvious from the code).

## Recommendation
VolatilityOracle should store "volume per liquidity" cumulative values (which do
not depend on any protocol parameter) instead of cumulative collected fees. Since
IV calculations use fggs and gammas in the following formula: fgg0 * gamma1 *
sqrt(P)
+
fgg1 * gamma0 / sqrt(P), cumulative values of fgg0 * gamma1 and
fgg1 * gamma0 might be stored, maybe even along with sqrt(P) terms as well,
which might also increase precision of calculations. Creating such cumulative
value(s) should be pretty straighforward.
