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
it will be reverted.

**test:**
```diff
  const VESTING_TIME = 43200; // Half a day

  const INCR = 2000;

  before(async () => {
    helper = new TestHelper();
    const { contracts, users } = await loadFixture(deployBondCalculatorFixture);

    bondCalculatorContract = contracts.bondCalculatorContract;
  });
  it("Should compute NumberTokenReal/NumberTokenExpected ratio", async () => {
    let ntrNtcRatio = await bondCalculatorContract.computeNtrDivNtc(
      1,
      VESTING_TIME,
+      1,
+      ethers.parseEther("43000"),
      ethers.parseEther("1000")
    );
    console.log(ntrNtcRatio);
```
```
$ npx hardhat test --grep "Calculator"
```
**Output:**
```
  Bond Calculator tests

    1) Should compute NumberTokenReal/NumberTokenExpected ratio
    ✓ Should compute the bond ROI
```
> And if `totalOutToken / 10 ** 18 > 43200`,
it will be passed.

**test:**
```diff
  const VESTING_TIME = 43200; // Half a day

  const INCR = 2000;

  before(async () => {
    helper = new TestHelper();
    const { contracts, users } = await loadFixture(deployBondCalculatorFixture);

    bondCalculatorContract = contracts.bondCalculatorContract;
  });
  it("Should compute NumberTokenReal/NumberTokenExpected ratio", async () => {
    let ntrNtcRatio = await bondCalculatorContract.computeNtrDivNtc(
      1,
      VESTING_TIME,
+      1,
+      ethers.parseEther("44000"),
      ethers.parseEther("1000")
    );
    console.log(ntrNtcRatio);
```
```
$ npx hardhat test --grep "Calculator"
```
**Output:**
```
  Bond Calculator tests
13243060n
    ✓ Should compute NumberTokenReal/NumberTokenExpected ratio
    ✓ Should compute the bond ROI
```
2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
Recommendation, Make sure that `ln(totalOutToken / 10 ** 18)` is bigger than `unsigned ln(timeRatio)`.<br>
For example:<br>
- if time is 43200 so `ln(totalOutToken / 10 ** 18) must be bigger than unsigned  ln(1/43200) => 15.3987436919` 
- if time is 432000 so `ln(totalOutToken / 10 ** 18) must be bigger than unsigned ln(1/432000) => 18.7206717868`
