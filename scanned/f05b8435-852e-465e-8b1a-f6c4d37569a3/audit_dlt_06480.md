# [H] FM_BC_Bancor_Redeeming_VirtualSupply_v1.setReserveRatioForSelling vulnerable to MEV

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-15
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/131
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** rnemes4
**Submission hash (on-chain):** 0x7c5051743724c53fbbf6588201971e815fe828fa6829ce1e27f0ae2ad4917ba1
**Severity:** high

**Description:**
**Description**\
`FM_BC_Bancor_Redeeming_VirtualSupply_v1.setReserveRatioForSelling` is susceptible to MEV attack if an attacker notices a reduction in the `reserverRatioForSelling` they could front run the transaction using a Flashloan to place a `buy` before the transaction and immediadetly `sell` after the transaction realising a profit in one transaction batch.

**Attack Scenario**\
with an initial setup
```Solidity
IFM_BC_Bancor_Redeeming_VirtualSupply_v1.BondingCurveProperties memory
            bc_properties = IFM_BC_Bancor_Redeeming_VirtualSupply_v1
                .BondingCurveProperties({
                formula: address(formula),
                reserveRatioForBuying: 333_333,
                reserveRatioForSelling: 333_333,
                buyFee: 0,
                sellFee: 0,
                buyIsOpen: true,
                sellIsOpen: true,
                initialIssuanceSupply: 1,
                initialCollateralSupply: 3
            });
```

1. Orchestrator calles `setReserveRatioForSelling` reducing the ratio from `333_333` to `333_133`
2. Bob see this transaction in the mempool and decides to front run with a `buy` for `1_000_000e18` using a flashloan
3. Bob then backrunsthe Orchestrators transaction creating a `sell` for `1_000_000e18`
4. Bob has made a profit of `1000010022715052240014003 - 1000000000000000000000000 = 10022715052240014003` in one transaction

**Attachments**

1. **Proof of Concept (PoC) File**
Add the following test to the E2E test suite which proves the scenario

```Solidity
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/131_
