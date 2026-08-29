# [H] Rebalancing Subsidy Exploit for Minor Leverage Deviations

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-07-03
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/314
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0xvd)

  **Beneficiary:** 0x23B5FbcF9dc2C5d5D6fDCd36d2239E6fC3aED2BA
  **Submission hash (on-chain):** 0xbabd50a7e9ad3d7b9e0010ad8b7b33b287a6dced27cf8c9a79d36978ad43143e
  **Severity:** high
  
  **Description:**
  **Description**\
The dLoop protocol implements a rebalancing mechanism that pays out subsidies to users who help bring the protocol's leverage back to its target ratio. 

However, there is a critical flaw in this design: the protocol pays out subsidies even for extremely minor deviations from the target leverage (e.g., 2.99X vs 3X).

This vulnerability allows attackers to continuously extract value from the protocol by performing unnecessary rebalancing operations. 

The issue is particularly severe because:

The subsidy is proportional to the TVL - as the protocol's TVL grows, the absolute value of the subsidy increases linearly.

There is no minimum deviation threshold required to qualify for a subsidy.

The protocol is planned for deployment on Sonic, where gas costs are minimal, making even small-profit exploits economically viable.

Each small oracle price change creates a new opportunity for exploitation, making this attack repeatedly executable.

The core issue is in the getCurrentSubsidyBps() function, which calculates subsidies directly proportional to the deviation from target leverage without any minimum threshold, and in the increaseLeverage() function, which enables collecting these subsidies

**Attack Scenario**\
An attacker can exploit this vulnerability through the following steps:

Monitor the dLoop vault for any deviation from target leverage (e.g., 2.99X vs target 3X).

When a deviation is detected (which can happen due to regular oracle price updates), call the increaseLeverage() function with the appropriate parameters.

Receive debt tokens that exceed the value of the supplied collateral tokens by the subsidy amount.

Repeat this process continuously as oracle prices fluctuate, creating new leverage deviations.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/314_
