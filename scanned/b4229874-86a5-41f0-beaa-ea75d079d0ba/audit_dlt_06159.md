# [H] Revert in the `computeRoi` function due to `ln`calculation

## Summary
Severity: High
Chain: Smart contract
Component: Convergence-Finance---IBO
Published: 2023-09-06
Source: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/47
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Submission hash (on-chain):** 0x7c402da62ea6108b6870add5bbba4ee087008c31a0397daa5ac077b560fe55be
**Severity:** high

**Description:**
**Description**\
The computeRoi function uses computeCvgExpected.
In the computeCvgExpected function, If `composedFunction`is 1, it uses `ln`:
```
else if (composedFunction == 1) {
            cvgExpected = ABDKMathQuad
                .ln(timeRatio)
                .div(ABDKMathQuad.ln(ABDKMathQuad.fromUInt(totalOutToken / 10 ** 18)))
                .add(ABDKMathQuad.fromUInt(1));
```
also as :`0 < timeRatio < 1`we have `-∞ < ln(timeRatio) <0`
, so we do `ln(timeRatio) / ln(totalOutToken / 10 ** 18)` to have <br>
`-1<ABDKMathQuad.ln(timeRatio).div(ABDKMathQuad.ln(ABDKMathQuad.fromUInt(totalOutToken / 10 ** 18))) < 0`,<br> but if `ln(totalOutToken / 10 ** 18)` is less than `ln(timeRatio)` so `ABDKMathQuad.ln(timeRatio).div(ABDKMathQuad.ln(ABDKMathQuad.fromUInt(totalOutToken / 10 ** 18)))` will become greater than -1 and `cvgExpected` becomes negative, so it causes revert in `computeRoi`.


**Impact**\
Revert in `computeRoi` may cause a lot of problems as `computeRoi` is used in `_depositRoi`(is used in `getBondView`) and `_computeCvgBondUsdPrice`( is used in `deposit` and `getBondView`)

- which makes `deposit` revert untill `ln(totalOutToken / 10 ** 18)` becomes bigger than `unsigned ln(timeRatio)`.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
In Bond Calculator tests:
`VESTING_TIME is: 43200`,
so
`log(1/43200) = -15.3987436919`,
so if 
`ln(totalOutToken / 10 ** 18) < 15.3987436919`,
it will be reverted.<br>
`ln(43200) = 15.3987436919`
so if `totalOutToken / 10 ** 18 < 43200`,

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/47_
