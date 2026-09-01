# [M] Precision Loss on the `computeCvgExpected` function

## Summary
Severity: Medium
Chain: Smart contract
Component: Convergence-Finance---IBO
Published: 2023-09-15
Source: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/74
Type: hats-finding

## Details
**Github username:** @Rotcivegaf
**Submission hash (on-chain):** 0x414bc79fbf80c70b6f86a48d67cef2314e3a4fc0c2f4ae9d8f7fd776eaf6a5a7
**Severity:** medium

**Description:**
**Description**

In the `computeCvgExpected` function there are two divisions that have loss of precision

If the `composedFunction` is not equal to `1`, loss 6 digits of precision when the `totalOutToken` is divided by 10 ** 6:

[`cvgExpected = cvgExpected.mul(ABDKMathQuad.fromUInt(totalOutToken / (TEN_POWER_6)));`](https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/blob/f43c5d9bc6b30c9f488e34836f09dc04d8f7361f/contracts/Bond/BondCalculator.sol#L76)

If the `composedFunction` is equal to `1`, add to the above, loss 18 digits of precision when the `totalOutToken` is divided by 10 ** 18:

[`.div(ABDKMathQuad.ln(ABDKMathQuad.fromUInt(totalOutToken / 10 ** 18)))`](https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/blob/f43c5d9bc6b30c9f488e34836f09dc04d8f7361f/contracts/Bond/BondCalculator.sol#L68)

**Attack Scenario**

The precision loss affect the functions `computeCvgExpectedUInt`, `computeNtrDivNtc` and the internal function `_computeNtrDivNtc` that is used in `computeRoi`

The function `computeRoi` is consulted by **Ibo** contract, in addition to being used for various view functions, the `computeRoi` is used by the function `deposit` miscalculating the `cvgToSold`

**Proof of Concept (PoC) Gist:** [https://gist.github.com/rotcivegaf/ff1947905f511419938b217b18c0c4eb](https://gist.github.com/rotcivegaf/ff1947905f511419938b217b18c0c4eb)

```solidity
const {expect} = require("chai");
const {loadFixture} = require("@nomicfoundation/hardhat-network-helpers");
const {deployBondCalculatorFixture} = require("../../fixtures/fixtures");

describe("PoC", function () {
    let bondCalculatorContract;
    const BOND_DURATION = 86_400 * 5;

    before(async () => {
        const {contracts } = await loadFixture(deployBondCalculatorFixture);
        bondCalculatorContract = contracts.bondCalculatorContract;
    });
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/74_
