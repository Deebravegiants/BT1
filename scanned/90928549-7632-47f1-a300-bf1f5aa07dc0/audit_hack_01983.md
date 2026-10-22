# [M] 5.2 Oracle Timestamps Not Checked

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Risk Accepted

The function getPrice does not verify that the round data received from Chainlink oracles is up-to-date.
If there is any problem with the oracles that results in outdated pricing data being returned. As a result
critical calculations for allowed borrowing and liquidations would become inaccurate. It might be possible
to liquidate safe positions or take out under-collateralized borrows.

Risk accepted:

Compound acknowledges the risk and notes that even if a defense against a lack of updates was
implemented, the ability to report false prices make the price oracles a primary risk vector for the
protocol. Moreover, Compound encourages governance to invest in improvements upon the oracle
system, especially ones which can also reduce gas costs.
