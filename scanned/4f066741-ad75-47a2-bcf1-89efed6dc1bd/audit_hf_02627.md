# [C] Denial-of-Service (DoS) During Manager Health Checks Affects Liquidations

## Summary
Severity: Critical
Contest weight: 0.3882
Dataset id: 14201
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Configured SVI feed bounds can cause denial-of-service (DoS) during Manager health checks, affecting liquidations.
SVI library calculates volume based on a chosen strike price. Certain values from configured bounds of a, forwardPrice, tao and strike variables will result in reverts in getVol() function reading accepted volume data. Reverts in SVI will prevent users from bidding in auctions on insolvent accounts, affecting liquidations.
Code comments located in the SVI.sol suggest that the following bounds are acceptable:
* @param strike desired strike for which to get vol for, in range [0, inf)
* @param a SVI parameter in range (-inf, inf)
* @param b SVI parameter in range [0, inf)
* @param rho SVI parameter in range (-1, 1)
* @param m SVI parameter in range (-inf, inf)
* @param sigma SVI parameter in range (0, inf)
* @param forwardPrice forward price in range [0, inf)
* @param tao time to expiry (in years) in range [0, inf)
However, the following exceptions will occur if parameters are set within these expected ranges:
• if strikePrice is set to zero, the function will revert with Overflow
• if forwardPrice exceeds type(uint56).max, the function will revert with Overflow
• if forwardPrice or tao are set to zero, the function will revert with division by modulo 0
• if a is set to a negative non-zero number, the function will revert with SVI_InvalidParameters
Since a, forwardPrice and tao variables are set during calls to LyraVolFeed.acceptData() where the feed owner has to approve signers to submit data, potential security implications are limited.
However, strike variable is controlled by those creating new options.
If a user accepts an option with zero value as strike price, it will cause an overflow in all LyraVolFeed.getVol() calculations. Subsequently, any call to StandardManager.getMarginAndMarkToMarket() will fail as well due to volFeeds[marketId].getVol() call on line [679].
During bids on insolvent auctions, the DutchAuction contract makes a call to ILiquidatableManager(manager).getMarginAndMarkToMarket(accountId, false, scenarioId) on line [6676], which will subsequently revert, preventing auctions on insolvent accounts to complete.

## Recommendation
Enforce forwardPrice, tao and strike to only accept non-zero values within their expected range and a to be a positive integer (including zero).
Derive (Formerly Lyra)
It is also recommended to revisit all SVI parameters bounds to ensure there are no inconsistencies between expected input into the library parameters and what values options might take on.
