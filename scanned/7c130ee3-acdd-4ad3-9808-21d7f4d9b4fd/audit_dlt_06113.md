# [H] Some stable velo pool oracles destabilize with massive swaps

## Summary
Severity: High
Chain: Smart contract
Component: VMEX
Published: 2023-08-03
Source: https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/issues/25
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0x57cb4226d489216ce6c5eda56f994c7ebc21c9b3f23f9c9cb171685c79c10a61
**Severity:** high severity

**Description:**
**Description**\
Swapping tokens in some stable velo pools (namely, the USDC/USDT pool, 0x2B47C794c3789f499D8A54Ec12f949EeCCE8bA16) causes the reported price by the oracle to change drastically. 

See below output of test
```
currentAsset:  0x2B47C794c3789f499D8A54Ec12f949EeCCE8bA16
Pricing  velo_USDTUSDC
Price:  BigNumber { value: "199993158704736408212" }
Naive pricing:  199993301239618960000
percent diff:  7.126987917041003e-7
stable
try swapping  0x7F5c764cBc14f9669B88837ca1490cCa17c31607
amount to swap:  5000000000
manip price 1:  BigNumber { value: "199995284623978362488" } percent diff:  0.000010629959823276315
Naive pricing after big swap:  2.605232473087505e+23
amount to swap:  25000000000
manip price 1:  BigNumber { value: "237505466159266789674" } percent diff:  0.1875679533114049
Naive pricing after big swap:  1.5626493404792083e+24
amount to swap:  125000000000
manip price 1:  BigNumber { value: "684396002421037701868" } percent diff:  2.4220970699875712
Naive pricing after big swap:  8.073279806331553e+24
```


**Attack Scenario**\
Flashloan huge amount of USDC, deposit to pool, overborrow on VMEX, repay flashloan.


1. **Proof of Concept (PoC) File (test suite)**


2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/issues/25_
