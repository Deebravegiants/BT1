# [M] dYdX incident: Twitter netizen "mhonkasalo" stated that there was a bug in the dYdX pledge contract. The user received 0 stkDYDX when pledged, th

## Summary
Severity: Medium
Target: dYdX
Loss: -
Attack method: Contract deployment error
Published: 2021-09-09
Source: https://twitter.com/dydxfoundation/status/1435641354860834816
Type: slowmist-incident

## Details
Twitter netizen "mhonkasalo" stated that there was a bug in the dYdX pledge contract. The user received 0 stkDYDX when pledged, the front end was disabled, and there were 64 affected addresses. Later, dYdX released the "Pledge Contract Bug" incident report. During the deployment of the upgradeable smart contract, the dYdX security module made an error, which caused the ratio of DYDX to stkDYDX to change from 1 to 0, so that users who pledged DYDX did not receive stkDYDX. dYdX stated that the error was caused by an error in the smart contract deployment process. It believed that there was no error in the code itself. The security module was previously audited by the smart contract, and based on the liquidity module design, the design was also audited. The security module is thoroughly tested before deployment. At present, user funds are safely locked in the security module until the end of the 28-day epoch, and no security module rewards are distributed and no withdrawals are possible. In order to restore the contract function, an upgrade is required. The suggested solution is to restore the security module function, allow the pledged user to retrieve the funds, and compensate the user for the wrong reward for participating in the security module.
