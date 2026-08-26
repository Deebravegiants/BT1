# [M] FM_BC_Bancor_Redeeming_VirtualSupply_v1 may get initialised in a way that will brick the contract

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-16
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/139
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** rnemes4
**Submission hash (on-chain):** 0xc4e1d972c648049ac67f27cf0ab33d445e5b01968a8160c3b54ba91721fb017e
**Severity:** medium

**Description:**
**Description**\
In the `FM_BC_Bancor_Redeeming_VirtualSupply_v1.init()` function it is possible to initialise with a combination of Issuance token decimals and initial issuance supply that will leave the contract in a state where it is impossible to call the `buy` function without it reverting.

**Attack Scenario**\
`init()` is called with an issuance token having 19 decimals and the virtualIssuanceSupply is set to 1 (in this scenraio it should have been set to at least 10)
Bob tries to make a `buy` with any deposit value, but the function will revert due to the code at line 400 returning zero:

```Solidity
FM_BC_Tools._convertAmountToRequiredDecimal(
                virtualIssuanceSupply, issuanceTokenDecimals, eighteenDecimals
            ),
```

being called with:
virtualIssuanceSupply = 1
issuanceTokenDecimals = 19
eighteenDecimals = 18

This will return 0 as proven by the following unit test

```Solidity
function testDecimalConversion() public {
        // Ensure the inputs are within valid ranges
        uint amount = 1;
        uint8 tokenDecimals = 19;
        uint8 requiredDecimals = 18;

        // Call the function with the base amount
        uint resultBase = _convertAmountToRequiredDecimal(
            amount,
            tokenDecimals,
            requiredDecimals
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/139_
