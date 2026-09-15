# [M] Lack of sensitivity for diversity between the spot price and safe price inside `verifyLSTPriceGap()` function due to rounding error

## Summary
Severity: Medium
Chain: Smart contract
Component: Tokemak
Published: 2024-03-06
Source: https://github.com/hats-finance/Tokemak-0x4a2d708ea6b0c04186ecb774cfad1e50fb5efc0b/issues/23
Type: hats-finding

## Details
**Github username:** @MatinR1
**Twitter username:** MatinRezaii1
**Submission hash (on-chain):** 0x7aba66d3a0b671cb0c28ebe1f22efcc15a787637965aa53307e2dbf878327469
**Severity:** medium

**Description:**
**Description**\

The function `verifyLSTPriceGap()` is designed to calculate the largest difference between spot & safe prices for the underlying tokens. It fetches both the safe and spot prices via the functions
`getPriceInEth()` and `getSpotPriceInEth()` respectively. In the case of a greater safe price over the spot price, the function checks to ensure the discrepancy is not exceeding the allowed tolerance.
This check is provided as follows inside the function [`verifyLSTPriceGap()`](https://github.com/hats-finance/Tokemak-0x4a2d708ea6b0c04186ecb774cfad1e50fb5efc0b/blob/74b397ce988a418a1bd02a45716cfc964922be26/src/strategy/LMPStrategy.sol#L435C21-L437C22):

```Solidity
    if (((priceSafe * 1.0e18 / priceSpot - 1.0e18) * 10_000) / 1.0e18 > tolerance) {
        return false;
    }
```

The problem arises from this point as the Solidity rounds down the result of an integer division, leading to a precision loss in output. If we want to precisely perform mathematical operations,
we should rearrange the mathematical to provide a more precise output.

Here we illustrate this math relation:

$$ \frac{\frac{\text{\large {priceSafe}} \times 10^{18}}{\text{\large {priceSpot}}} - 10^{18}}{10^{18}} \times 10000 > \text{tolerance} $$

The actual implementation contains some divisions and also a priority of division over multiplication that truncates the precision in the output. We can rearrange the abovementioned relation
into the following relation:

$$ \frac{\text{priceSafe} \times 10^{18} - \text{priceSpot} \times 10^{18}}{\text{priceSpot} \times 10^{18}} \times 10000 > \text{tolerance} $$

We can also simplify one more step without sacrificing the precision of the prices:

$$ (\text{priceSafe} \times 10^{18} - \text{priceSpot} \times 10^{18}) \times 10000 > \text{tolerance} \times {\text{priceSpot} \times 10^{18}} $$

With this method, we can eliminate the division and check the two spot and safe prices more precisely than the actual implementation.

Now, the impact of such a precision loss is illustrated. We consider these two prices and want to observe the behavior of the function `verifyLSTPriceGap()` to see whether it is
preventing the execution or not:

```Solidity
       uint priceSafe = 1.0e18;
       uint priceSpot = 9.9896e17;
```

With these inputs, the function returns us `true` and continues the execution. But if we calculate it precisely we can see that it exceeds the allowed tolerance and must return `false` instead.

In the case of not rendering the latex formulas, I've created a picture from the mentioned relations:

![Equations](https://github.com/MatinR1/MatinR1/blob/main/TokemakEquation.PNG)



**Attack Scenario**\
Describe how the vulnerability can be exploited.

**Attachments**

1. **Proof of Concept (PoC) File**
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {Test, console2} from "forge-std/Test.sol";
import {console} from "forge-std/console.sol";


contract MathTest is Test {

    uint public tolerance;

    function setUp() external {

        tolerance = 10; // 10 bps mock tolerance considered in this test
    }

    /// @notice A mock function representing the actual implementation of
    ///         price diversity comparator inside the LMPStrategy.sol contract
    /// @param priceSafe the safe price which is fetched by getPriceInEth()
    /// @param priceSpot the spot price which is fetched by getSpotPriceInEth()
    /// @return a boolean showing the comparison result
    function priceComparitor_actual(uint priceSafe, uint priceSpot) public view returns(bool) {

        return (((priceSafe * 1.0e18 / priceSpot - 1.0e18) * 10_000) / 1.0e18 > tolerance);
    }

    /// @notice A mock function representing the precise implementation of
    ///         price diversity comparator inside the LMPStrategy.sol contract
    /// @param priceSafe the safe price which is fetched by getPriceInEth()
    /// @param priceSpot the spot price which is fetched by getSpotPriceInEth()
    /// @return a boolean showing the comparison result
    function priceComparitor_accurate(uint priceSafe, uint priceSpot) public view returns(bool) {

        return (((priceSafe * 1.0e18) - (priceSpot * 1.0e18)) * 10_000) > (tolerance  * 1.0e18 * priceSpot);
    }

    function test_precissionLoss() public {

        uint priceSafe = 1.0e18;
        uint priceSpot = 9.9896e17;

        bool comparison_actual = priceComparitor_actual(priceSafe, priceSpot);
        bool comparison_accurate =priceComparitor_accurate(priceSafe, priceSpot);
        
        console.log("Current Implementation: ", comparison_actual);
        console.log("Actual Implementation:  ", comparison_accurate);
    }

}

2. **Revised Code File (Optional)**

Rewrite the formula using this relation:

```Solidity
    if ((((priceSafe * 1.0e18) - (priceSpot * 1.0e18)) * 10_000) > (tolerance  * 1.0e18 * priceSpot)) {
        return false;
    }
```
  
**Files:**
  - TokemakPOC.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmVfYiLa2WXzmZzVRAgnLr3ZBA2THqWAmtW57GmuvT2NYJ)
