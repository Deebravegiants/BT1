# [M] FM_BC_Bancor_Redeeming_VirtualSupply_v1.sol#getStaticPriceForBuying() - potential precision loss due to supported ERC20's decimals

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/59
Type: hats-finding

## Details
**Github username:** @PlamenTSV
**Twitter username:** @p_tsanev
**Submission hash (on-chain):** 0x6eba57f01ed5dc80118751ae878308cefd1df4ba050c7fa7b79a4419a437931e
**Severity:** medium

**Description:**
**Description**\
The ``getStaticPriceForBuying()`` and ``getStaticPriceForSelling()``
are a core part of the Funding Manager's bonding curve, since it calculates the price of buying and selling issuance tokens against the specified collateral token. The formula used is ``Aragon's BatchedBancorMarketMaker`` formula, which in the current context of the codebase is prone to rounding errors.

**Attack Scenario**\
The formula looks like this: ``uint(PPM) * uint(PPM) * virtualCollateralSupply
            / (virtualIssuanceSupply * uint(reserveRatioForBuying))``

It uses the PPM = 1_000_000 variable in order to raise the precision of the numerator when multiplying it by the supply of the collateral token.
The denominator is simply the multiplication of the issuance token supply and the ratio for either buying or selling.
The problem arises in the differences between the 2 reserves.
Inside ``VirtualCollateralSupplyBase_v1`` when we invoke ``_addVirtualCollateralAmount``, we add the collateral as a raw amount, meaning it keeps its decimals inside the supply. The same goes for issuance. In the scenario where the collateral has much less decimals than the issuance, we can round down the price to 0.

E.g:
Collateral - USDC/USDT = 1e6 decimals
PPM is 1e6, thus inside the formula it will be 1e12 when multiplied by itself, meaning that the numerator will be in 1e18 decimals.
If the issuance token is >=18 decimals, which is supported per the system specifications, we can have the denominator being 18 or more decimals.
Considering the value of ``reserveRatioForBuying``, which inside the tests was coded to 333_333 ~ 1e5 decimals, leads to our denominator being far greater than the numerator and the price rounding to 0.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**

**Recommendation**\
As a remediation I see 2 possibilities:
1. Normalize the 2 supplies to the same decimal space before running the price calculation
2. Either change the PPM variable to something larger, or multiply the numerator by 1e18 when calculating price and when issuing tokens, divide by 1e18
