# [M] 5.2.1 StrategyFloorFromChainlinkwill often revert due to stale prices

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** StrategyFloorFromChainlink.sol
**Description:** TheFloorFromChainlinkstrategy inherits fromBaseStrategyChainlinkPriceLatency, so it can
have amaxLatencyof at most 3600 seconds. However, all of the chainlink mainnet floor price feeds have a
heartbeat of 86400 seconds (24 hours), so the chainlink strategies will revert with thePriceNotRecentEnough
error quite often. At the time of writing, every single mainnet floor price feed has anupdateAttimestamp well over
3600 seconds in the past, meaning the strategy would always revert for any mainnet price feed right now. This may
have not been realized earlier because the Goerli floor price feedsdohave a heartbeat of 3600, but the mainnet
heartbeat is much less frequent.
One of the consequences is that users might miss out on exchanges they would have accepted. For example, if
a taker bid is interested in a maker ask with an eth premium from the floor, in the likely scenario where the taker
didn't log-in within 1 hour of the last oracle update, the strategy will revert and the exchange won't happen even
though both parties are willing. If the floor moves up again the taker might not be interested anymore. The maker
will have lost out on making a premium from the floor, and the taker would have lost out on the exchange they were
willing to make.
**Recommendation:** For theFloorFromChainlinkstrategy, allow for amaxLatencyvalue of 86400, instead of
restricting at 3600.
**LooksRare:** Fixed in PR 326.
**Spearbit:** Verified.
