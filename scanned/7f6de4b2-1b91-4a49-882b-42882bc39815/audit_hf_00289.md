# [M] Late users will take more losses than expected when the underlying contract

## Summary
Severity: Medium
Contest weight: 0.1078
Dataset id: 1464
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Even though it’s unlikely in practice, but in theory, the underlying contract (`EthAnchor`) may suffer investment losses and causing decreasing of the PPS of AUST token. (There are codes that considered this situation in the codebase. eg. handling of `depositShares > claimerShares`).

However, when this happens, the late users will suffer more losses than expected than the users that withdraw earlier. The last few users may lose all their funds while the first users can get back 100% of their deposits.

## Proof of Concept
// ### for deposits: d1, d2, d3, the beneficiary are: c1, c2, c2
    depositAmount          claimerShares
d1: + 100e18           c1: + 100e36
d2: + 100e18           c2: + 100e36
d3: + 100e18           c2: + 100e36

    depositAmount of d1, d2, d3 = 100e18
    c1 claimerShares: 100e36
    c2 claimerShares: 200e36
    total shares: 300e36

    // ### when the PPS of AUST drop by 50% 
    totalUnderlyingMinusSponsored: 300e18 -> 150e18

    // ### d2 withdraw
    c2 claimerShares: 200e36
    d2 depositAmount: 100e18
    d2 depositShares: 300e36 * 100e18 / 150e18 = 200e36

    Shares to reduce: 200e36
    c2 claimerShares: 200e36 -> 0
    c2 totalPrincipal: 200e18 -> 100e18
    totalShares: 300e36 -> 100e36

    underlying.safeTransfer(d2, 100e18)
    totalUnderlyingMinusSponsored: 150e18 -> 50e18

## Recommendation
In order to properly handle the investment loss of the strategy, consider adding a new storage variable called `totalLoss` to maintain a stable value of `share / adjustedUnderlying`.
    
    adjustedUnderlying = underlying + totalLoss

This is a classic medium risk when using the definition provided by Code4rena:
 
`2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.`
