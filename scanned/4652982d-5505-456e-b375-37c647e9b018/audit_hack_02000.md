# [H] 7.1 Chainlink Query May Revert

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

The Pool contract relies on ChainLink assumptions that do not hold. Chainlink's round IDs do not always
increase monotonically. Therefore, the getRoundData queries can revert. Relying on _roundId-- in
GeometricBrownianMotionOracle.getHistoricalPrice is not correct, since querying an invalid
ID will make the swap revert.

Code corrected:

The call to the price feed's getRoundData function has been moved in a try/catch block and the
function returns (0, 0) if the oracle call reverts.
