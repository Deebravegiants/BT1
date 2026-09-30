# [M] Divide before multiply

## Summary
Severity: Medium
Contest weight: 0.1113
Dataset id: 354
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Here you have more information: <https://gist.github.com/alexon1234/e5038a9f66136ae210be692f8803d874>

**[strictly-scarce (vader) questioned](https://github.com/code-423n4/2021-04-vader-findings/issues/255#issuecomment-830631408):**

Can’t quite understand the assertion that a division is made before a multiply in the code outlined
     
     
    uint _units = (((P * part1) + part2) / part3);
    return (_units * slipAdjustment) / one;  // Divide by 10**18

`_units` will be `0 -> 2**256`. `slipAdjustment` will be `0 -> 10**18` `one` is `10**18`
     
     
    // returns 0
    return (0 * 10**18) / 10**18;
    return (2**256 * 0) / 10**18;
    return (<10**9 * <10**9) / 10**18;
    // returns  non-zero
    return (>=10**9 * >=10**9) / 10**18;

## Recommendation
No recommendation
