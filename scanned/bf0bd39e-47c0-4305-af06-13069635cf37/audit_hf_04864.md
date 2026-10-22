# [H] getTokenFShare will never increase past floor

## Summary
Severity: High
Contest weight: 0.7653
Dataset id: 22763
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In FairSideNetwork - getTokenFShare() is used to get the FSHARE to calculate the
FSD token spot price getFSDPrice. The spot price is used to calculate the amount
the user needs to pay when paying for membership cover and requesting claims.
However, the getTokenFShare calculation of total cost share benefits is incorrect
which leads the FSHARE to always be the floor price 2500 ETH.
The formula for calculating the fshare is as follows:
https://github.com/FairSideNetwork/FairsideContractsV2/blob/main/2/contracts/network/FairSideNetwork.sol#L929
```solidity
function getTokenFShare() internal view returns (uint256) {
    uint256 fShare = totalPWPCSB.mul(100) / fsd.gearingFactor();
    // Floor of 2500 ETH
    if (fShare < getFshareFloor()) fShare = getFshareFloor();
    return fShare;
}
```
Notice that totalPWPCSB.mul(100) is using ABDK math. The result of
totalPWPCSB.mul(100) actually divides totalPWPCSB by 1e16 instead. This is because
mul multiplies totalPWPCSB and 100 then scales down 1e18.
Even if the maximum amount of coverage (100 ETH) is purchased by 1 billion users,
the resultant fshare is much under the floor value (2500 ether):
```solidity
uint256(1_000_000_000 * 100 ether).mul(100) = 10000000000000 (0.00001 ether)
```
Fshare will never represent a price on the curve as it's supposed to. Incorrect price
will be set for purchasing cover and requesting coverage.

## Recommendation
If using ABDK math, use totalPWPCSB.mul(100 ether) instead. However, no need to
use ABDK math here and can just multiply by 100 (totalPWPCSB * 100) like in
https://github.com/FairSideNetwork/FairsideContractsV2/blob/main/2/contracts/token/ABC.sol#L57C54-L57C60
