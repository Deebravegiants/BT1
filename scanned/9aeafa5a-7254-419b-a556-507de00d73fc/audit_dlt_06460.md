# [H] Precision Loss in Fee Calculation Due to Integer Division

## Summary
Severity: High
Chain: Smart contract
Component: Metrom
Published: 2024-05-20
Source: https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/issues/6
Type: hats-finding

## Details
**Github username:** @0xShax2nk
**Twitter username:** 0xShashanks_07
**Submission hash (on-chain):** 0x036d447ecc25e5da5c15a600d29fe4b8da568fa0b187bac125bf847b19133d7b
**Severity:** high

**Description:**
**Description**\
The Metrom smart contract calculates fees as a percentage of the reward amount using integer division. Due to the nature of integer division in Solidity, any non-integer result is truncated, resulting in a loss of precision. This can lead to scenarios where the calculated fee amount rounds down to zero, especially when dealing with small reward amounts.

**Impact**

The impact of this precision loss issue is twofold:

Economic Impact: The contract owner may not receive the intended fees for facilitating campaigns, leading to potential revenue loss. This is particularly significant if numerous small reward campaigns are created, as the cumulative loss of fees could be substantial.

Incentive Misalignment: Users may be incentivized to create campaigns with rewards small enough to avoid fees, which could lead to an increase in such campaigns and an unintended usage pattern of the platform.

**Attack Scenario**\
An attacker could exploit this issue by repeatedly creating campaigns with reward amounts that are calculated to result in a fee amount that rounds down to zero. For example:

The attacker sets up a campaign with a reward amount of 50 tokens.     The global fee percentage is 1% (represented as 10,000 in contract terms).     The fee calculation is 50 * 10,000 / 1,000,000 = 0 after integer division.     The attacker creates multiple such campaigns, each time avoiding the fee.

By scaling this strategy, the attacker can significantly reduce the cost of running campaigns on the platform, effectively exploiting the service without paying the intended fees.


**Recommendation**

To address this issue, the following recommendations are proposed:

Minimum Fee: Implement a minimum fee amount that is charged for any campaign creation to ensure that the contract owner receives compensation for all campaigns.

Fixed-Point Arithmetic: Utilize a fixed-point arithmetic library or implement a custom solution to handle fee calculations with greater precision.

Rounding Method: Adjust the fee calculation to round up to the nearest whole number when the result is not an integer. This can be done by adding UNIT - 1 before dividing by UNIT:

`uint256 _feeAmount = (_amount * _fee + UNIT - 1) / UNIT;`
