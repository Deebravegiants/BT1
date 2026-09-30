# [M] dYdX incident: DeFi Derivatives Agreement dYdX released an investigation report on the deposit contract accident on November 27, stating that the

## Summary
Severity: Medium
Target: dYdX
Loss: $ 211,000
Attack method: Contract Vulnerability
Published: 2021-11-27
Source: https://dydx.exchange/blog/deposit-proxy-post-mortem
Type: slowmist-incident

## Details
DeFi Derivatives Agreement dYdX released an investigation report on the deposit contract accident on November 27, stating that there has been a serious loophole in the agent smart contract that has been handling deposits to the dYdX exchange since November 24. At around 12:00 UTC on the 27th, dYdX The team performed a white hat hacking operation to save vulnerable user funds, totaling approximately US$2 million. These funds are sent to a non-custodial escrow contract, and only the original owner of these funds can retrieve them. However, when the dYdX team performed the white hat hacking operation, an estimated $211,000 of funds was used by the MEV robot, and the user has now been fully compensated.
