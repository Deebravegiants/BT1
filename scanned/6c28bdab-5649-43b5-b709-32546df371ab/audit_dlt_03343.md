# [M] Flash minting and burning can reduce the paid fees when purchasing a membership or opening a cost share request

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-fairside
Published: 2021-05-27
Source: https://github.com/code-423n4/2021-05-fairside-findings/issues/76
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

Users can pay fewer FSD tokens when purchasing a membership or opening a cost share request by flash minting and burning FSD tokens, which could significantly affect the FSD spot price.

## Proof of Concept

The function `getFSDPrice` returns the current FSD price based on the reserves in the capital pool (see lines 353-364 in contract `FSDNetwork`). Notice that when minting and burning FSD tokens, the `fsd.getReserveBalance()` increases but not the `fShare`. Therefore, according to the pricing formula, `FairSideFormula.f`, the FSD price increases when minting, and vice versa, decreases when burning.

When purchasing a membership, the number of FSD tokens that a user should pay is calculated based on the current FSD price, which is vulnerable to manipulation by flash minting and burning. Consider a user performing the following actions (all are done within a single transaction or flashbot bundle):

1. The user mints a large number of FSD (by using flash loans) to raise the current FSD price.
2. The user purchases a membership by calling `purchaseMembership`. Since the price of FSD is relatively high, the user pays fewer FSD tokens for the membership fee than before.
3. The user burns the previously minted FSD tokens, losing 3.5% of his capital for the tribute fees.

Although the user pays for the 3.5% tribute fees, it is still possible to make a profit. Suppose that the price of FSD to ETH is `p_1` and `p_2` before and after minting, respectively. The user purchases a membership with `x` ETH `costShareBenefit`, and uses `y` ETH to flash mint the FSD tokens. In a regular purchase, the user pays `0.04x / p_1` FSD tokens, equivalent to `0.04x` ETH. By performing flash mints and burns, the user pays `0.04x / p_2` FSD tokens, which is, in fact, equivalent to `0.04x * p_1 / p_2` ETH. He also pays `0.035y` ETH for tribute fees. The profit user made is `0.04x * (1 - p1 / p2) - 0.035y` (ETH), where `p2` and `y` are dependent to each other but independent to `x`. Thus, the profit can be positive if `costShareBenefit` is large enough.

The same vulnerability exists when a user opens a cost share request, where the `bounty` to pay is calculated based on the current price of FSD tokens.

Referenced code:
[FSDNetwork.sol#L353-L364](http://github.com/code-423n4/2021-05-fairside/blob/main/contracts/network/FSDNetwork.sol#L353-L364)
[FSDNetwork.sol#L145-L146](https://github.com/code-423n4/2021-05-fairside/blob/main/contracts/network/FSDNetwork.sol#L145-L146)
[FSDNetwork.sol#L217-L222](https://github.com/code-423n4/2021-05-fairside/blob/main/contracts/network/FSDNetwork.sol#L217-L222)

## Recommended Mitigation Steps

Force users to wait for (at least) a block to prevent flash minting and burning.
